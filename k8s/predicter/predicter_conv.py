# model
from lstm_conv import LSTMConv
import tensorflow as tf
import pandas as pd
import numpy as np

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
import traceback
import random
import os


def setup_metrics(collector_registry):
    execution_time = Summary(
        "predicter_execution_time",
        "Total execution time the Predicter has been running",
        registry=collector_registry,
    )
    measure_amount = Counter(
        "predicter_measure_amount",
        "Total amount of measures read from Cassandra",
        registry=collector_registry,
    )
    last_success = Gauge(
        "predicter_last_success",
        "Unixtime Predicter job last succeeded",
        registry=collector_registry,
    )
    return execution_time, measure_amount, last_success


def create_cassandra_connection(
    cassandra_user,
    cassandra_passsword,
    cassandra_url,
    cassandra_port,
    cassandra_keyspace,
    cassandra_src_table,
):
    auth_provider = PlainTextAuthProvider(
        username=cassandra_user, password=cassandra_passsword
    )
    cluster = Cluster([cassandra_url], port=cassandra_port, auth_provider=auth_provider)
    session = cluster.connect(keyspace=cassandra_keyspace)

    retrieve_query = f"SELECT id, \
                        product_id, \
                        timestamp, \
                        model, \
                        country, \
                        company, \
                        subscription, \
                        price \
                        FROM {cassandra_keyspace}.{cassandra_src_table} \
                        WHERE model = '{product_model}' \
                        AND product_id = {product_id} \
                        AND company = '{company}' \
                        AND subscription = '{product_sub}' \
                        AND country = '{country}' \
                        ALLOW FILTERING;"

    # statement = SimpleStatement(query, fetch_size=1000)
    retrieve_prepared = session.prepare(retrieve_query, keyspace=cassandra_keyspace)

    return cluster, session, retrieve_prepared


def reorganize_data(data, company):
    colnames = [
        "id",
        "product_id",
        "timestamp",
        "model",
        "country",
        "company",
        "subscription",
        "price",
    ]
    data_frame = pd.DataFrame(data, columns=colnames)
    del data

    reorg = (
        data_frame.reset_index()
        .groupby(["timestamp", "company"])["price"]
        .first()
        .unstack()
        .reset_index()
        .set_index("timestamp")
    )

    timestamps = pd.DataFrame(
        index=pd.date_range(reorg.index[0], reorg.index[-1], freq="D")
    )
    reorg = pd.merge(timestamps, reorg, left_index=True, right_index=True, how="left")
    reorg.columns.name = None
    reorg.interpolate(method="time", inplace=True, limit_direction="both")

    X, Y = [], []
    raw_data = reorg[company]

    for i in range(len(raw_data)):
        end_ix = i + 6

        if end_ix > len(raw_data) - 1:
            break

        seq_x, seq_y = raw_data[i:end_ix], raw_data[end_ix]

        X.append(seq_x)
        Y.append(seq_y)

    X = np.array(X)
    Y = np.array(Y)

    value = int(len(X) * 0.7)
    
    x_train, y_train = X[:value], Y[:value]
    x_test, y_test = X[value:], Y[value:]

    x_train = x_train.reshape((x_train.shape[0], 2, 1, 6 // 2, 1))
    x_test = x_test.reshape((x_test.shape[0], 2, 1, 6 // 2, 1))

    # fit = (X[:value], Y[:value])
    # test = (X[value:], Y[value:])

    # x_train = fit[0].reshape((fit[0].shape[0], seq, 1, steps // 2, features))
    # x_test = test[0].reshape((test[0].shape[0], seq, 1, steps // 2, features))

    fit = (x_train, y_train)
    test = (x_test, y_test)

    return fit, test


def store_processed_measures(
    cassandra_session, cassandra_keyspace, cassandra_dst_table, results
):
    timestamp = datetime.now()
    cassandra_session.execute(
        f"INSERT INTO {cassandra_keyspace}.{cassandra_dst_table} \
            (product_id, timestamp, model, country, company, subscription, prediction) \
            VALUES ({product_id}, \
            '{timestamp}', \
            '{product_model}', \
            '{country}', \
            '{company}', \
            '{product_sub}', \
            {[item for sublist in results for item in sublist]})"
    )


if __name__ == "__main__":
    """
    for local testing
        port forward
            cassandra
    """

    os.environ["PYTHONHASHSEED"] = "0"
    os.environ["TF_DETERMINISTIC_OPS"] = "1"
    random.seed(1234)
    np.random.seed(1234)
    tf.random.set_seed(1234)
    tf.keras.utils.set_random_seed(1234)
    tf.config.experimental.enable_op_determinism()

    cassandra_url = "localhost"
    cassandra_port = 9042
    cassandra_user = "cron_user"
    cassandra_passsword = "cron_password"
    cassandra_keyspace = "zenprice"
    cassandra_src_table = "pickle_data"
    cassandra_dst_table = "pickle_results"
    product_model = "samsung Galaxy A51 128GB"
    product_id = 93
    product_sub = "unlocked"
    company = "Abcdin"
    country = "CL"
    pushgateway_url = "localhost" 
    pushgateway_port = 9091
    instance_log_id = "X"

    # cassandra_url = os.getenv("CASSANDRA_URL")
    # cassandra_port = os.getenv("CASSANDRA_PORT")
    # cassandra_user = os.getenv("CASSANDRA_USER")
    # cassandra_passsword = os.getenv("CASSANDRA_PASSWORD")
    # cassandra_keyspace = os.getenv("CASSANDRA_KEYSPACE")
    # cassandra_src_table = os.getenv("CASSANDRA_SRC_TABLE")
    # cassandra_dst_table = os.getenv("CASSANDRA_DST_TABLE")
    # product_model = os.getenv("PRODUCT_MODEL")
    # product_id = os.getenv("PRODUCT_ID")
    # product_sub = os.getenv("PRODUCT_SUB")
    # company = os.getenv("COMPANY")
    # country = os.getenv("COUNTRY")
    # pushgateway_url = os.getenv("PUSHGATEWAY_URL")
    # pushgateway_port = os.getenv("PUSHGATEWAY_PORT")
    # instance_log_id = os.getenv("INSTANCE_LOG_ID")

    if cassandra_port is not None:
        cassandra_port = int(cassandra_port)
    else:
        cassandra_port = 9042

    collector_registry = CollectorRegistry()
    execution_time, measure_amount, last_success = setup_metrics(collector_registry)

    (
        cassandra_cluster,
        cassandra_session,
        prepared_retrieve_statement,
    ) = create_cassandra_connection(
        cassandra_user,
        cassandra_passsword,
        cassandra_url,
        cassandra_port,
        cassandra_keyspace,
        cassandra_src_table,
    )

    model = LSTMConv(n_seq=2, n_steps=6 // 2, n_features=1)

    try:
        with execution_time.time():
            data = []

            print("Querying data from Cassandra...")
            for rows in cassandra_session.execute(prepared_retrieve_statement):
                data.append(rows)
            measure_amount.inc(len(data))

            print("Reorganizing data...")
            fit, test = reorganize_data(data, company)

            print("Training model...")
            model.fit(
                data_x=fit[0],
                data_y=fit[1],
                validation_data=test,
                epochs=100,
                batch_size=72,
                verbose=1,
                shuffle=False,
            )

            print("Predicting values...")
            results = model.predict(test[0])

            print("Storing measures in Cassandra...")
            store_processed_measures(
                cassandra_session, cassandra_keyspace, cassandra_dst_table, results
            )

    except:
        print(traceback.format_exc())

    finally:
        print("Sending metrics...")
        last_success.set_to_current_time()
        pushadd_to_gateway(
            f"{pushgateway_url}:{pushgateway_port}",
            job=f"predicter_convolutional_{instance_log_id}_{company}_{country}_{product_model}",
            registry=collector_registry,
        )

        cassandra_session.shutdown()
        cassandra_cluster.shutdown()
