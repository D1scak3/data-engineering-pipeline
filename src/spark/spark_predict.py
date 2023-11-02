# argument parser
from argparse import ArgumentParser, FileType

# pyspark
from pyspark.sql import SparkSession

# model
from dummy_model import DummyModel
import tensorflow as tf
import pandas as pd
import numpy as np

# cassandra
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import SimpleStatement

# standard libs
import os
import random
from datetime import datetime

def pandas_factory(colnames, rows):
    return pd.DataFrame(rows, columns=colnames)


if __name__ == "__main__":
    """
    Spark task to import deltas from kafka and append them to a provided table.

    steps:
        read data from kafka
        read data from cassandra
        train model
        predict data 
        store data on cassandra

    python3 delta_predict.py -m "samsung Galaxy A51 128GB" -p 93 -c Abcdin -q CL -k zenprice -s unlocked -n pickle_predictions
    """

    os.environ["PYTHONHASHSEED"] = "0"
    os.environ["TF_DETERMINISTIC_OPS"] = "1"
    random.seed(1234)
    np.random.seed(1234)
    tf.random.set_seed(1234)

    # parse arguments
    parser = ArgumentParser()

    # cassandra details for data retrieving
    parser.add_argument("-m", "--model", required=True)
    parser.add_argument("-p", "--product-id", required=True)
    parser.add_argument("-c", "--company", required=True)
    parser.add_argument("-q", "--qountry")
    parser.add_argument("-k", "--keyspace", required=True)
    parser.add_argument("-n", "--name", required=True)
    parser.add_argument("-s", "--subscription", required=True)
    # parser.add_argument("-q", "--query", required=True, type=FileType("r"))
    args = parser.parse_args()

    # create spark session
    spark_session = SparkSession.builder.appName(args.name).getOrCreate()

    # connect to cassandra
    print("CONNECTING TO CASSANDRA...")
    auth_provider = PlainTextAuthProvider(username='cassandra', password='cassandra')
    cluster = Cluster(["127.0.0.1"], port=9042, auth_provider=auth_provider)
    session = cluster.connect(args.keyspace)
    print(f"CONNECTION TO KEYSPACE {args.keyspace} ESTABLISHED.")

    # query data
    query = f"SELECT id, \
                product_id, \
                timestamp, \
                model, \
                country, \
                company, \
                subscription, \
                price \
                FROM pickle_data \
                WHERE model = '{args.model}' \
                AND product_id = {args.product_id} \
                AND company = '{args.company}' \
                AND subscription = '{args.subscription}' \
                AND country = '{args.qountry}' \
                ALLOW FILTERING;" 
    statement = SimpleStatement(query, fetch_size=1000)
    prepared = session.prepare(query)

    print("QUERYING FOR DATA...")
    data = []
    for rows in session.execute(statement):
        data.append(rows)
    # len data = 477

    colnames = ["id", "product_id", "timestamp", "model", "country", "company", "subscription", "price"]
    data = pd.DataFrame(data, columns=colnames)

    # reorganize data
    print("REORGANIZING DATA")
    reorg = data.reset_index() \
        .groupby(["timestamp", "company"])["price"] \
        .first() \
        .unstack() \
        .reset_index() \
        .set_index("timestamp")

    timestamps = pd.DataFrame(index = pd.date_range(reorg.index[0], reorg.index[-1], freq="D"))
    reorg = pd.merge(timestamps, reorg, left_index=True, right_index=True, how="left")
    reorg.columns.name = None
    reorg.interpolate(method="time", 
                      inplace=True,
                      limit_direction="both")

    X = []
    Y = []
    raw_data = reorg[args.company]

    for i in range(len(raw_data)):
        end_ix = i + 7

        if end_ix > len(raw_data) - 1:
            break

        seq_x, seq_y = raw_data[i:end_ix], raw_data[end_ix]

        X.append(seq_x)
        Y.append(seq_y)

    X = np.array(X)
    Y = np.array(Y)

    value = int(len(X) * 0.7)
    fit = (X[:value], Y[:value])
    test = (X[value:], Y[value:])

    # create model, fit, and predict
    print("CREATING MODEL")
    model = DummyModel(n_steps=7, n_features=1)

    print("FITTING MODEL...")
    model.fit(data_x=fit[0], 
                    data_y=fit[1], 
                    validation_data=test,
                    epochs=100, 
                    batch_size=72, 
                    verbose=1, 
                    shuffle=False)

    print("PREDICTING RESULTS...")
    results = model.predict(test[0])
    print("PREDICT COMPLETED!!!")
    # print(results)
    # input(...)
    # len results = 141
    
    # save data to cassandra
    print("CHECKING IF TABLE EXISTS...")
    rows = session.execute("SELECT table_name FROM system_schema.tables;")
    flag = False
    for row in rows:
        if args.name in row:   # table already exists
            flag = True
    
    if flag is False:               # table does not exist
        print("TABLE DOES NOT EXIST.\nCREATING TABLE...")
        session.execute(f"CREATE TABLE {args.name} \
                        (product_id int PRIMARY KEY, \
                        timestamp timestamp, \
                        model varchar, \
                        country varchar, \
                        company varchar, \
                        subscription varchar, \
                        prediction list<float>);")
        print("TABLE CREATED.")

    print("WRITING DATA TO TABLE...")
    timestamp = datetime.now()  #.strftime(r"%d-%m-%Y %H:%M:%S.")
    session.execute(f"INSERT INTO {args.name} (product_id, timestamp, model, country, company, subscription, prediction) \
                    VALUES ({args.product_id}, '{timestamp}', '{args.model}', '{args.qountry}', '{args.company}', '{args.subscription}', {[item for sublist in results for item in sublist]})")
        
    print("WRINTING COMPLETED.\nCLOSING SPARK.")
