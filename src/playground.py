import os
import random
import numpy as np
import pandas as pd
import json
import tensorflow as tf
from spark.lstm_simple import LstmSimple

from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider


if __name__ == "__main__":
    """
    Spark task to import deltas from kafka and predict values.
    Data will also be xtracted from cassandra in order to fit the model
    and predict the values of the provided deltas.

    Data will also be extracted from cassandra in order to fit the model
    and predict the values of the provided deltas.

    Data is assumed to have the following input schema:
        [
            {
                "updated_timestamp": [id, "brand", "model", price, "currency", "subscription"]
            }
        ]

    Data on cassandra will be updated witht he new values AND the prediction.
    """

    # setup seeds for deterministic values
    os.environ["PYTHONHASHSEED"] = "0"
    os.environ["TF_DETERMINISTIC_OPS"] = "1"
    random.seed(1234)
    np.random.seed(1234)
    tf.random.set_seed(1234)


    # with open("../data/exported/exported_data.tsv", "r") as file:
    #     with open("../data/exported/sanitized_data.tsv", "w") as f:
    #         for line in file:
    #             new = line.strip("\n").split("\t")
    #             new.remove("")
    #             string = "\t".join(new)
    #             f.write(string + "\n")



    #--------------lstm model--------------
    data = pd.read_pickle("../data/long_product_group_id_23")
    print(data)

    # main_id	price_id	plan_id	product_id	created_at	updated_at	brand	model	value	currency	plan_type	
    # data = pd.read_table("../data/exported/exported_data.tsv", delimiter="\t", on_bad_lines="skip")
    # print(data)
    # input(...)

    # schema {"id":1,"id":1,"id":1,"created_at":"2020-01-12T22:51:23.830513","updated_at":"2020-01-12T22:51:23.830513","value":"199990","currency":"CLP","plan_type":"unlocked"}
    # data = pd.read_json("../data/exported/json_exported.json")
    # for x in data:
    #         print(x)
    # print(data)
    # input(...)

    # product_model = None
    # for x in data["product"]:
    #     product_model = x
    #     break
    # print(product_model)
    # input(...)

    # print(data)
    # input(...)
    # for x in data["product"]:
    #     print(x)
    # input(...)

    # print(len(data))
    # input(...)

    model = LstmSimple(data, n_steps=7, n_features=1, train_percent=0.7, company="Abcdin")
    model.fit(epochs=100, batch_size=72, verbose=1, shuffle=False)
    # model.save_model("saved_models", "lstm")
    # input(...)
    model.load_model("saved_models", "lstm.zip")
    result = model.predict()

    performance = model.performance_compare(result)
    print(performance)

    # with open("output_adapted.txt", "w") as file:
    #     file.write(f"Performance: {performance}")
    #     for x in result:
    #         file.write(str(x) + "\n")

    
    #--------------kafka--------------
    # kafka_config = {}
    # kafka_config["bootstrap.servers"] = "localhost:9092"
    # kafka_config["group.id"] = "postgres_data"
    # kafka_config["auto.offset.reset"] = "earliest"


    # print(f"test \'{9}")

    # #--------------cassandra--------------
    # # # create session
    # auth_provider = PlainTextAuthProvider(username='cassandra', password='cassandra')
    # cluster = Cluster(["127.0.0.1"], port=9042, auth_provider=auth_provider)
    # session = cluster.connect("zenprice")

    # # create keyspace
    # # session.execute("CREATE KEYSPACE IF NOT EXISTS zen_price WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 2 };")
    # # session.execute("CREATE ROLE zenprice with password='zenprice' and login=true;")

    # file = open("../data/exported/json_exported.json")
    # values = json.load(file)

    # print("Checking if table exists...")
    # rows = session.execute("SELECT table_name FROM system_schema.tables;")
    # flag = False
    # for row in rows:
    #     print(row)
    #     if "zenprice_values" in row:   # table already exists
    #         flag = True
    
    # if flag is False:               # table does not exist
    #     print("Table does no exist.\nCreating table...")
    #     session.execute("CREATE TABLE zenprice_values (id int PRIMARY KEY, brand varchar, model varchar, price decimal, color varchar, subscription varchar, created_timestamp timestamp, updated_timestamp timestamp);")

    # print("Writing data to table...")
    # for value in values:                  # write values to cassandra
    #     session.execute(f"INSERT INTO zenprice_values (id, brand, model, price, color, subscription, created_timestamp, updated_timestamp) VALUES ({value[0]}, {value[1]}, {value[2]}, {value[3]}, {value[4]}, {value[5]}, {value[6]}, {value[7]})")
        

