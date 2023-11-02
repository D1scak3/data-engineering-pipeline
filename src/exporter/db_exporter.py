# postgres
import psycopg2 as psql

# kafka
from confluent_kafka import Producer
from configparser import ConfigParser

# argument parser
from argparse import ArgumentParser, FileType


def delivery_callback(err, msg):
    if err:
        print(f"ERROR: Message delivery failed: {err}")
    else:
        if int(msg.key().decode("utf-8")) % 1000 == 0:
            print(f"Produced 1000 events.")


if __name__ == "__main__":
    """
    Script to extract data from a Postgres database and send it to a Kafka topic.
    """
    
    # parse arguments
    parser = ArgumentParser()
    parser.add_argument("-c", "--config_file", type=FileType("r"))  # kafka config
    parser.add_argument("-t", "--topic", default="postgres_data")   # kafka topic
    parser.add_argument("-i", "--ip", default="127.0.0.1")          # postgres ip
    parser.add_argument("-p", "--port", default=5432)               # postgres port
    parser.add_argument("-q", "--query", type=FileType("r"))        # postgres query
    args = parser.parse_args()

    # kafka config parse
    config_parser = ConfigParser()
    config_parser.read_file(args.config_file)
    config = dict(config_parser["exporter"])
    producer = Producer(config)
    topic = args.topic

    # postgres config parse
    ip = args.ip
    port = args.port
    query = args.query.read()
    print("CONNECTING TO POSTGRES...")
    conn = psql.connect(database="postgres", user="postgres", password="mysecretpassword", host="localhost", port="5432")

    # run postgres query
    print("QUERYING FOR DATA...")
    cur = conn.cursor()
    cur.execute(query)

    # print(f"There are {cur.arraysize} records.")

    # send data to kafka
    # each record is a tuple of data
    print("READING DATA and WRITING TO KAFKA...")
    counter = 1
    for record in cur:
        value = ""
        for x in record:
            value += str(x)
            value += "\t"

        # print(f"{counter}\t{value}")
        producer.produce(topic, value=value, key=str(counter), callback=delivery_callback)
        counter += 1
        producer.poll(1)
        if counter >= 10000:
            break
        # producer.flush()  # only necessary if writes are meant to be synchronous

    print("DONE WRITTING TO KAFKA.")
    print("CLOSING EVERYTHING.")
    cur.close()
    conn.close
