# kafka
from argparse import ArgumentParser, FileType
from confluent_kafka import Consumer, KafkaError, KafkaException

# cassandra
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

# argument parser
from argparse import ArgumentParser

# standard libs
import time


if __name__ == "__main__":
    """
    Spark task to import data from kafka to cassandra
    Data processing (reorganize) will be done here.
    Data is assumed to have the following input schema:
        [{id, brand, model, price, color, subscription, created_timestamp, updated_timestamp}]
    Data will be written to cassandra with the following schema:
        [id, brand, model, price, color, subscription, created_timestamp, updated_timestamp]
    """

    # parse arguments
    parser = ArgumentParser()
    parser.add_argument("-t", "--topic", default="postgres_data")
    parser.add_argument("-g", "--consumer_group", default="default_consumer_group")
    parser.add_argument("-i", "--ip", default="broker")
    parser.add_argument("-p", "--port", default=9092)
    parser.add_argument("-n", "--name", default="database")
    args = parser.parse_args()

    # create kafka consumer
    kafka_config = {}
    print(f"URL:{args.ip}:{args.port}")
    # kafka_config["bootstrap.servers"] = f"{args.ip}:{args.port}"
    kafka_config ["bootstrap.servers"] = "127.0.0.1:29092"
    kafka_config["group.id"] = args.consumer_group
    kafka_config["auto.offset.reset"] = "earliest"
    consumer = Consumer(kafka_config)

    # read data from kafka
    # values = []
    # timer = 0
    # try:
    #     print("CONNECTING TO KAFKA...")
    #     consumer.subscribe([args.topic])
    #     print("CONNECTED TO KAFKA.")

    #     print("STARTING TO READ VALUES...")
    #     while True:
    #         msg = consumer.poll(timeout=5.0)
    #         if msg is None: 
    #             timer += 1
    #             time.sleep(1)

    #         # if msg.error():
    #         #     if msg.error().code() == KafkaError._PARTITION_EOF:
    #         #         # End of partition event
    #         #         sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
    #         #                          (msg.topic(), msg.partition(), msg.offset()))
    #         #         break
    #         #     elif msg.error():
    #         #         raise KafkaException(msg.error())

    #         else:
    #             topic = msg.topic()
    #             key = msg.key().decode("utf-8")
    #             value = msg.value().decode("utf-8")
    #             values.append(value.strip("\n").split("\t"))

    #             timer = 0

    #             if len(values) % 1000 == 0:
    #                 print("READ 1000 VALUES...")

    #         if timer >= 10:
    #             break
                
    # finally:
    #     consumer.close()

    # read data from tsv file
    values = []
    with open("../../data/exported/exported_data.tsv", "r") as file:
        for line in file:
            if len(values) == 1000:
                break
            values.append(line.strip("\n").split("\t"))   # 11 rows

    # id   id   id   id   created   updated   brand   model   price   currency   subscription
    # save data to cassandra
    auth_provider = PlainTextAuthProvider(username='cassandra', password='cassandra')
    cluster = Cluster(["localhost"], port=9042, auth_provider=auth_provider)
    session = cluster.connect(keyspace="zenprice")

    # check if table exists
    print("CHECKING IF TABLE EXISTS...")
    rows = session.execute("SELECT table_name FROM system_schema.tables WHERE keyspace_name='zenprice';")
    flag = False
    for row in rows:
        if args.name in row:
            print("TABLE ALREADY EXISTS.")
            flag = True
    
    if flag is False:
        print("TABLE DOES NOT EXIST.\nCREATING TABLE...")
        session.execute(f"CREATE TABLE {args.name} (id int PRIMARY KEY, \
                        price_id int, \
                        plan_id int, \
                        product_id int, \
                        created_timestamp timestamp, \
                        updated_timestamp timestamp, \
                        brand varchar, \
                        model varchar, \
                        price decimal, \
                        currency varchar, \
                        subscription varchar);")
        print("TABLE CREATED.")

    print("WRITING DATA TO TABLE...")
    for value in values:
        query = f"INSERT INTO {args.name} (id, price_id, plan_id, product_id, created_timestamp, updated_timestamp, brand, model, price, currency, subscription) \
                        VALUES ({value[0]}, {value[1]}, {value[2]}, {value[3]}, '{value[4]}', '{value[5]}', '{value[6]}', '{value[7]}', {value[8]}, '{value[9]}', '{value[10]}')"
        # print(query)
        # input(...)
        session.execute(query)

    print("WRINTING COMPLETED.\nCLOSING SPARK.")
