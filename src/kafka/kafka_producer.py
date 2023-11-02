#!/usr/bin/env python

from random import choice
from argparse import ArgumentParser, FileType
from configparser import ConfigParser
from confluent_kafka import Producer

import pandas as pd


def delivery_callback(err, msg):
    if err:
        print('ERROR: Message failed delivery: {}'.format(err))
    else:
        print("Produced event to topic {topic}: key = {key:12} value = {value:12}".format(
            topic=msg.topic(), key=msg.key().decode('utf-8'), value=msg.value().decode('utf-8')))


if __name__ == '__main__':
    # Parse the command line.
    parser = ArgumentParser()
    parser.add_argument('config_file', type=FileType('r'))
    args = parser.parse_args()

    # Parse the configuration.
    config_parser = ConfigParser()
    config_parser.read_file(args.config_file)
    config = dict(config_parser['default'])

    # Create Producer instance
    producer = Producer(config)


    # # read and send data to topic
    # with open("processed_data.tsv", "r", encoding="utf-8") as file:
    #     file.readline()
    #     topic = "measurements"
    #     count = 0
    #     for line in file:
    #         split = line.strip("\n").split("\t")
    #         # print(count)
    #         producer.produce(topic, line, split[0], callback=delivery_callback)
    #         producer.poll()
    #         if count == 100000:
    #             # producer.poll(100000)
    #             producer.flush()
    #             count = 0
    #         else:
    #             count += 1

    topic = "random_values"
    # data = pd.read_pickle("../Data/long_product_group_id_23")
    while True:
        value = input("Insere valor:")
        producer.produce(topic, value=value, key="0", callback=delivery_callback)
        producer.poll(1)
        producer.flush()


    # # Produce data by selecting random values from these lists.
    # topic = "purchases"
    # user_ids = ['eabara', 'jsmith', 'sgarcia', 'jbernard', 'htanaka', 'awalther']
    # products = ['book', 'alarm clock', 't-shirts', 'gift card', 'batteries']

    # count = 0
    # for _ in range(10):

    #     user_id = choice(user_ids)
    #     product = choice(products)
    #     producer.produce(topic, product, user_id, callback=delivery_callback)
    #     count += 1

    # # Block until the messages are sent.
    # producer.poll(10000)
    # producer.flush()