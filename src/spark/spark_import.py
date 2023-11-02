# kafka
from argparse import ArgumentParser
from confluent_kafka import Consumer

# cassandra
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

# argument parser
from argparse import ArgumentParser

# standard
import time
import datetime


if __name__ == "__main__":
    """
    Spark task to import data from kafka to cassandra
    Data processing (reorganize) will be done here.

    Data schema is dependant on postgres and cassandra, so it will be assumed to be like:
        received data:
            [{id, brand, model, price, color, subscription, created_timestamp, updated_timestamp}]
        written data:
            {id, brand, model, price, color, subscription, created_timestamp, updated_timestamp}
    
    python3 db_import.py -t pickle_data -i 127.0.0.1 -p 29092 -k zenprice -n pickle_data -g g1
    """

    """
    KAFKA_URL
    KAFKA_PORT
    KAFKA_TOPIC
    KAFKA_CONSUMER_GROUP
    CASSANDRA_USER
    CASSANDRA_PASSWORD
    CASSANDRA_KEYSPACE
    CASSANDRA_TABLE
    """

    # parse arguments
    parser = ArgumentParser()
    parser.add_argument("-t", "--topic", default="postgres_data")
    parser.add_argument("-g", "--consumer_group", default="default_consumer_group")
    parser.add_argument("-i", "--ip", default="broker")
    parser.add_argument("-p", "--port", default=9092)
    parser.add_argument("-k", "--keyspace", default="default_keyspace")
    parser.add_argument("-n", "--name", default="database")
    args = parser.parse_args()

    # create kafka consumer
    kafka_config = {}
    print(f"URL:{args.ip}:{args.port}")
    kafka_config["bootstrap.servers"] = f"{args.ip}:{args.port}"
    # kafka_config ["bootstrap.servers"] = "127.0.0.1:29092"
    kafka_config["group.id"] = args.consumer_group
    kafka_config["auto.offset.reset"] = "earliest"
    consumer = Consumer(kafka_config)

    # read data from kafka
    values = []
    # colnames = ["product_id", "timestamp", "brand", "model", "country", "company", "subscription", "currency", "price"]
    # dframe = pd.DataFrame(columns=colnames)
    timer = 0
    try:
        print("CONNECTING TO KAFKA...")
        consumer.subscribe([args.topic])
        print("CONNECTED TO KAFKA.")

        print("STARTING TO READ VALUES...")
        while True:
            msg = consumer.poll(timeout=5.0)
            if msg is None: 
                timer += 1
                time.sleep(1)

            # if msg.error():
            #     if msg.error().code() == KafkaError._PARTITION_EOF:
            #         # End of partition event
            #         sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
            #                          (msg.topic(), msg.partition(), msg.offset()))
            #         break
            #     elif msg.error():
            #         raise KafkaException(msg.error())

            else:
                topic = msg.topic()
                key = msg.key().decode("utf-8")
                value = msg.value().decode("utf-8")
                value = value.strip("\n").split("\t")
                # print(value)
                # value = [0 if (isinstance(x, numbers.Number) and math.isnan(x)) else x for x in value]
                # print(value)
                # while len(value) < 9:
                #     value.append(None)
                if len(value) < 8:
                    print("continue")
                    continue
                values.append(value)
                # dframe = pd.concat([dframe, value])
                # print(dframe)
                # input(...)

                timer = 0

                if len(values) % 1000 == 0:
                    print("READ 1000 VALUES...")

            if timer >= 5:
                # dframe = pd.DataFrame(values, columns=colnames)
                # dframe[["price"]] = dframe[["price"]].fillna(method="ffill")
                break
                
    finally:
        consumer.close()

    # for x in values:
    #     print(x)
    
    # exit()

    # save data to cassandra
    auth_provider = PlainTextAuthProvider(username='cassandra', password='cassandra')
    # cluster = Cluster(["cassandra-seed", "cassandra-node-a", "cassandra-node-b"], port=9042, auth_provider=auth_provider)
    cluster = Cluster(["localhost"], port=9042, auth_provider=auth_provider)
    session = cluster.connect(keyspace=args.keyspace)

    # check if table exists
    print("CHECKING IF TABLE EXISTS...")
    rows = session.execute(f"SELECT table_name FROM system_schema.tables WHERE keyspace_name='{args.keyspace}';")
    flag = False
    for row in rows:
        if args.name in row:
            print("TABLE ALREADY EXISTS.")
            flag = True
    
    if flag is False:
        print("TABLE DOES NOT EXIST.\nCREATING TABLE...")
        # created_timestamp timestamp, \
        # session.execute(f"CREATE TABLE {args.name} (main_id int PRIMARY KEY, \
        #                 price_id int, \
        #                 plan_id int, \
        #                 product_id int, \
        #                 updated_timestamp timestamp, \
        #                 brand varchar, \
        #                 model varchar, \
        #                 price decimal, \
        #                 currency varchar, \
        #                 country varchar, \
        #                 company varchar, \
        #                 subscription varchar);")
        
        session.execute(f"CREATE TABLE {args.name} \
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
    query = f"INSERT INTO {args.name} (id, timestamp, product_id, model, country, company, product_group_id, subscription, price) \
            VALUES (uuid(), ? ,? ,? ,? ,? ,? ,?, ?)"
    prepared_statement = session.prepare(query)

    for row in values:
        product_id = int(row[0])
        timestamp = datetime.datetime.strptime(row[1], r"%Y-%m-%d %H:%M:%S")
        product_group_id = int(row[5])
        # price = 0.0 if row[7] == "nan" else float(row[7])
        price = float(row[7])

        session.execute(prepared_statement, (timestamp, product_id, str(row[2]), str(row[3]), str(row[4]), product_group_id, str(row[6]), price))

    print("WRINTING COMPLETED.\nCLOSING SPARK.")
