# kafka
from confluent_kafka import Producer
from configparser import ConfigParser

# argument parser
from argparse import ArgumentParser, FileType

import pandas as pd


def delivery_callback(err, msg):
    if err:
        print(f"ERROR: Message delivery failed: {err}")
    else:
        quant = int(msg.key().decode("utf-8"))
        if quant % 1000 == 0 and quant > 0:
            print(f"Produced 1000 events.")


if __name__ == "__main__":
    """
    Send data manually to a kafka topic.

    python3 manual_exporter.py -c exporter_conf.ini -t pickle-data -f long_product_group_id_23
    """

    # parse arguments
    parser = ArgumentParser()
    parser.add_argument("-c", "--config_file", type=FileType("r"))  # kafka config
    parser.add_argument("-t", "--topic", default="postgres_data")  # topic to write data
    parser.add_argument("-f", "--file", required=True)  # data file
    args = parser.parse_args()

    # kafka config parse
    config_parser = ConfigParser()
    config_parser.read_file(args.config_file)
    config = dict(config_parser["exporter"])
    producer = Producer(config)
    topic = args.topic

    data = pd.read_pickle(args.file)
    data = data.values.tolist()
    for idx, row in enumerate(data):
        string = "\t".join([str(x) for x in row])
        # print(string)
        producer.produce(topic, value=string, key=str(idx), callback=delivery_callback)
        producer.poll()
        # producer.flush() # if producer is meant to be synchronous
