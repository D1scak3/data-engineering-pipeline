# kafka
from confluent_kafka import Consumer

# cassandra
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

# prometheus
from prometheus_client import Gauge, CollectorRegistry, push_to_gateway, pushadd_to_gateway

# standard
import time
from datetime import datetime
from os import getenv
from logging import info


if __name__ == "__main__":
    """
    Import data from a a provided kafka broker and moves it to a provided cassandra table.

    important metrics:
        setup time(load configs, establish connections)
        time to import data
        time to store data
        total execution time
        amount of measures

    get envs
    setup collector registry
    setup kafka config
    connect to kafka
    connect to cassandra
    while true
        get msgs
        if full
            store cass
        elif timeout
            close kafka connection
            store cass
        else
            continue
    close kafka connection
    close cassandra connection



    python3 db_import.py -t pickle_data -i 127.0.0.1 -p 29092 -k zenprice -n pickle_data -g g1
    """


    kafka_url = getenv("KAFKA_URL")
    kafka_port = getenv("KAFKA_PORT")
    kafka_topic = getenv("KAFKA_TOPIC")
    kafka_consumer_group = getenv("KAFKA_CONSUMER_GROUP")
    cassandra_url = getenv("CASSANDRA_URL")
    cassandra_port = getenv("CASSANDRA_PORT")
    cassandra_user = getenv("CASSANDRA_USER")
    cassandra_password = getenv("CASSANDRA_PASSWORD")
    cassandra_keyspace = getenv("CASSANDRA_KEYSPACE")
    cassandra_table = getenv("CASSANDRA_TABLE")
    pushgatway_url = getenv("PUSHGATEWAY_URL")
    pushgateway_port = getenv("PUSHGATEWAY_PORT")


    # metric collection prep
    # hist = Histogram(name=f'importer_{kafka_topic}_duration_seconds', )
    # duration.observe()
    registry = CollectorRegistry()
    duration = Gauge(f'importer_{kafka_topic}_duration_seconds', f'Duration of {kafka_topic} import job', registry=registry)
    measure_quant = Gauge(f"importer_{kafka_topic}_measure_amount", f"Amount of metrics collected from {kafka_topic} import job", registry=registry)


    # create kafka consumer
    kafka_config = {}
    info(f"URL:{kafka_url}:{kafka_port}")
    kafka_config["bootstrap.servers"] = f"{kafka_url}:{kafka_port}"
    kafka_config["group.id"] = kafka_consumer_group
    kafka_config["auto.offset.reset"] = "earliest"
    consumer = Consumer(kafka_config)


    # measure retrieval from kafka
    try:
        with duration.time():

            values = []
            timer = 0

            info("CONNECTING TO KAFKA...")
            consumer.subscribe([kafka_topic])
            info("CONNECTED TO KAFKA.")

            info("STARTING TO READ VALUES...")
            while True:
                msg = consumer.poll(timeout=5.0)
                if msg is None: 
                    timer += 1
                    time.sleep(1)

                else:
                    topic = msg.topic()
                    key = msg.key().decode("utf-8")
                    value = msg.value().decode("utf-8")
                    value = value.strip("\n").split("\t")

                    if len(value) < 8:
                        info("continue")
                        continue
                    values.append(value)

                    timer = 0

                    if len(values) % 1000 == 0:
                        info("READ 1000 VALUES...")

                if timer >= 5:
                    break

            consumer.close()
            measure_quant.set(len(values))


            # save data to cassandra
            auth_provider = PlainTextAuthProvider(username='cassandra', password='cassandra')
            cluster = Cluster([cassandra_url], port=int(cassandra_port), auth_provider=auth_provider)
            session = cluster.connect(keyspace=cassandra_keyspace)


            # check if table exists
            info("CHECKING IF TABLE EXISTS...")
            rows = session.execute(f"SELECT table_name FROM system_schema.tables WHERE keyspace_name='{cassandra_keyspace}';")
            flag = False
            for row in rows:
                if cassandra_table in row:
                    info("TABLE ALREADY EXISTS.")
                    flag = True

            if flag is False:
                info("TABLE DOES NOT EXIST.\nCREATING TABLE...")
                session.execute(f"CREATE TABLE {cassandra_table} \
                                (id uuid PRIMARY KEY, \
                                timestamp timestamp, \
                                product_id int, \
                                model varchar, \
                                country varchar, \
                                company varchar, \
                                product_group_id int, \
                                subscription varchar, \
                                price float);")
                info("TABLE CREATED.")


            # writing data to table
            info("WRITING DATA TO TABLE...")
            query = f"INSERT INTO {cassandra_table} (id, timestamp, product_id, model, country, company, product_group_id, subscription, price) \
                    VALUES (uuid(), ? ,? ,? ,? ,? ,? ,?, ?)"
            prepared_statement = session.prepare(query)

            for row in values:
                product_id = int(row[0])
                timestamp = datetime.strptime(row[1], r"%Y-%m-%d %H:%M:%S")
                product_group_id = int(row[5])
                price = float(row[7])

                session.execute(prepared_statement, (timestamp, product_id, str(row[2]), str(row[3]), str(row[4]), product_group_id, str(row[6]), price))

            info("WRINTING COMPLETED.\n.")

            session.shutdown()
            cluster.shutdown()

    except:
        pass

    else:
        last_success = Gauge('mybatchjob_last_success', 
        'Unixtime my batch job last succeeded', registry=registry)
        last_success.set_to_current_time()

    finally:
        pushadd_to_gateway(f'{pushgatway_url}:{pushgateway_port}', job=f'importer_{kafka_topic}', registry=registry)