# kafka
from confluent_kafka import Consumer

# cassandra
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

# standard
import time
import datetime
import os


if __name__ == "__main__":
    """
    Import data from a a provided kafka broker and moves it to a provided cassandra table.

    python3 db_import.py -t pickle_data -i 127.0.0.1 -p 29092 -k zenprice -n pickle_data -g g1
    """

    kafka_url = os.getenv("KAFKA_URL")
    kafka_port = os.getenv("KAFKA_PORT")
    kafka_topic = os.getenv("KAFKA_TOPIC")
    kafka_consumer_group = os.getenv("KAFKA_CONSUMER_GROUP")
    cassandra_url = os.getenv("CASSANDRA_URL")
    cassandra_port = os.getenv("CASSANDRA_PORT")
    cassandra_user = os.getenv("CASSANDRA_USER")
    cassandra_password = os.getenv("CASSANDRA_PASSWORD")
    cassandra_keyspace = os.getenv("CASSANDRA_KEYSPACE")
    cassandra_table = os.getenv("CASSANDRA_TABLE") 


    # create kafka consumer
    kafka_config = {}
    print(f"URL:{kafka_url}:{kafka_port}")
    kafka_config["bootstrap.servers"] = f"{kafka_url}:{kafka_port}"
    kafka_config["group.id"] = kafka_consumer_group
    kafka_config["auto.offset.reset"] = "earliest"
    consumer = Consumer(kafka_config)


    # read data from kafka
    values = []
    timer = 0
    try:
        print("CONNECTING TO KAFKA...")
        consumer.subscribe([kafka_topic])
        print("CONNECTED TO KAFKA.")

        print("STARTING TO READ VALUES...")
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
                    print("continue")
                    continue
                values.append(value)

                timer = 0

                if len(values) % 1000 == 0:
                    print("READ 1000 VALUES...")

            if timer >= 5:
                break
                
    finally:
        consumer.close()


    # save data to cassandra
    auth_provider = PlainTextAuthProvider(username='cassandra', password='cassandra')
    cluster = Cluster([cassandra_url], port=cassandra_port, auth_provider=auth_provider)
    session = cluster.connect(keyspace=cassandra_keyspace)


    # check if table exists
    print("CHECKING IF TABLE EXISTS...")
    rows = session.execute(f"SELECT table_name FROM system_schema.tables WHERE keyspace_name='{cassandra_keyspace}';")
    flag = False
    for row in rows:
        if cassandra_table in row:
            print("TABLE ALREADY EXISTS.")
            flag = True

    if flag is False:
        print("TABLE DOES NOT EXIST.\nCREATING TABLE...")
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
        print("TABLE CREATED.")

    print("WRITING DATA TO TABLE...")
    query = f"INSERT INTO {cassandra_table} (id, timestamp, product_id, model, country, company, product_group_id, subscription, price) \
            VALUES (uuid(), ? ,? ,? ,? ,? ,? ,?, ?)"
    prepared_statement = session.prepare(query)

    for row in values:
        product_id = int(row[0])
        timestamp = datetime.datetime.strptime(row[1], r"%Y-%m-%d %H:%M:%S")
        product_group_id = int(row[5])
        price = float(row[7])

        session.execute(prepared_statement, (timestamp, product_id, str(row[2]), str(row[3]), str(row[4]), product_group_id, str(row[6]), price))

    print("WRINTING COMPLETED.\n.")
