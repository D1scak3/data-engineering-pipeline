# kafka
from confluent_kafka import Consumer, KafkaException

# cassandra
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster

# prometheus
from prometheus_client import (
    pushadd_to_gateway,
    CollectorRegistry,
    Counter,
    Summary,
    Gauge,
)

# standard
from datetime import datetime
from logging import info
from os import getenv
import traceback


def setup_metrics(collector_registry):
    # import_time = Counter("import_time", "", registry=collector_registry)
    # store_time = Gauge("store_time", "", registry=collector_registry)
    execution_time = Summary(
        "importer_execution_time",
        "Total execution time the Importer has been running",
        registry=collector_registry,
    )
    measure_amount = Counter(
        "importer_measure_amount",
        "Total amount of measures read from Kafka",
        registry=collector_registry,
    )
    last_success = Gauge(
        "importer_predicter_last_success",
        "Unixtime Predicter job last succeeded",
        registry=collector_registry,
    )
    return execution_time, measure_amount, last_success


def create_kafka_consumer(kafka_url, kafka_port, kafka_consumer_group):
    kafka_config = {}
    kafka_config["bootstrap.servers"] = f"{kafka_url}:{kafka_port}"
    kafka_config["group.id"] = kafka_consumer_group
    kafka_config["auto.offset.reset"] = "smallest" # smallest=read from beggining|largest=read from most recent msg
    kafka_config["enable.auto.commit"] = "true" # true=offsets are updated | false=offsets are not updated
    # kafka_config["auto.offset.reset"] = "earliest"
    return Consumer(kafka_config)


def create_cassandra_connection(
    cassandra_user,
    cassandra_password,
    cassandra_url,
    cassandra_port,
    cassandra_keyspace,
    cassandra_table,
):
    auth_provider = PlainTextAuthProvider(
        username=cassandra_user, password=cassandra_password
    )
    cluster = Cluster([cassandra_url], port=cassandra_port, auth_provider=auth_provider)
    session = cluster.connect(keyspace=cassandra_keyspace)
    query = f"INSERT INTO {cassandra_table} (id, timestamp, product_id, model, country, company, product_group_id, subscription, price) \
                    VALUES (uuid(), ? ,? ,? ,? ,? ,? ,?, ?)"
    prepared_statement = session.prepare(query)
    return cluster, session, prepared_statement


def store_values(cassandra_session, values, prepared_statement):
    for row in values:
        product_id = int(row[0])
        timestamp = datetime.strptime(row[1], r"%Y-%m-%d %H:%M:%S")
        product_group_id = int(row[5])
        price = float(row[7])

        cassandra_session.execute(
            prepared_statement,
            (
                timestamp,
                product_id,
                str(row[2]),
                str(row[3]),
                str(row[4]),
                product_group_id,
                str(row[6]),
                price,
            ),
        )


if __name__ == "__main__":
    """
    for local testing:
        kubectl port-forward svc/cassandra 9042:9042 -n cassandra
        kubectl port-forward svc/pushgateway-svc 9091:9091 -n monitoring
    """

    # kafka_url = "192.168.49.6"
    # kafka_port = 9095
    # kafka_topic = "pickle-data"
    # kafka_consumer_group = "local_group"
    # measure_batch_size = 1000
    # cassandra_url = "localhost"
    # cassandra_port = 9042
    # cassandra_user = "cron_user"
    # cassandra_password = "cron_password"
    # cassandra_keyspace = "zenprice"
    # cassandra_table = "pickle_data"
    # pushgateway_url = "localhost"
    # pushgateway_port = 9091
    # instance_log_id = "local"

    kafka_url = getenv("KAFKA_URL")
    kafka_port = getenv("KAFKA_PORT")
    kafka_topic = getenv("KAFKA_TOPIC")
    kafka_consumer_group = getenv("KAFKA_CONSUMER_GROUP")
    measure_batch_size = getenv("MEASURE_BATCH_SIZE")
    cassandra_url = getenv("CASSANDRA_URL")
    cassandra_port = getenv("CASSANDRA_PORT")
    cassandra_user = getenv("CASSANDRA_USER")
    cassandra_password = getenv("CASSANDRA_PASSWORD")
    cassandra_keyspace = getenv("CASSANDRA_KEYSPACE")
    cassandra_table = getenv("CASSANDRA_TABLE")
    pushgateway_url = getenv("PUSHGATEWAY_URL")
    pushgateway_port = getenv("PUSHGATEWAY_PORT")
    instance_log_id = getenv("INSTANCE_LOG_ID")

    if measure_batch_size is not None:
        measure_batch_size = int(measure_batch_size)
    else:
        measure_batch_size = 1000

    if cassandra_port is not None:
        cassandra_port = int(cassandra_port)
    else:
        cassandra_port = 9042

    collector_registry = CollectorRegistry()
    execution_time, measure_amount, last_success = setup_metrics(collector_registry)

    kafka_consumer = create_kafka_consumer(kafka_url, kafka_port, kafka_consumer_group)
    kafka_consumer.subscribe([kafka_topic])
    (
        cassandra_cluster,
        cassandra_session,
        prepared_statement,
    ) = create_cassandra_connection(
        cassandra_user,
        cassandra_password,
        cassandra_url,
        cassandra_port,
        cassandra_keyspace,
        cassandra_table,
    )

    try:
        with execution_time.time():
            values = []
            amount = 0

            while True:
                msg = kafka_consumer.poll(timeout=10.0)

                if msg is None:
                    print("No more measures to read. Saving last measures to Cassandra...")
                    store_values(cassandra_session, values, prepared_statement)
                    values.clear()
                    measure_amount.inc(amount)
                    break

                if msg.error():
                    raise KafkaException(msg.error())

                else:
                    amount += 1
                    topic = msg.topic()
                    key = msg.key().decode("utf-8")
                    value = msg.value().decode("utf-8")
                    value = value.strip("\n").split("\t")

                    if len(value) != 8:
                        continue

                    values.append(value)

                    if len(values) >= measure_batch_size:
                        print("Writing measures to Cassandra...")
                        store_values(cassandra_session, values, prepared_statement)
                        values.clear()

    except Exception as e:
        print(repr(e))
        print("\n")
        print(traceback.format_exc())

    finally:
        print("Sending metrics...")
        last_success.set_to_current_time()
        pushadd_to_gateway(
            f"{pushgateway_url}:{pushgateway_port}",
            job=f"importer_{instance_log_id}_{kafka_topic}",
            registry=collector_registry,
        )

        print("Closing connections.")
        kafka_consumer.close()
        cassandra_session.shutdown()
        cassandra_cluster.shutdown()
