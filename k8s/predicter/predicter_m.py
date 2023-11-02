# model
from k8s.predicter.lstm_simple import LSTMSimple
import tensorflow as tf
import pandas as pd
import numpy as np

# cassandra
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import SimpleStatement
from cassandra.policies import DCAwareRoundRobinPolicy

# prometheus
from prometheus_client import Gauge, CollectorRegistry, pushadd_to_gateway

# standard libs
import os
import random
import logging
from datetime import datetime


if __name__ == "__main__":
    """
    Read data from cassandra based on provided input, train model, and predict next value.

    python3 delta_predict.py -m "samsung Galaxy A51 128GB" -p 93 -c Abcdin -q CL -k zenprice -s unlocked -n pickle_predictions
    """


    # set seeds to static values
    os.environ["PYTHONHASHSEED"] = "0"
    os.environ["TF_DETERMINISTIC_OPS"] = "1"
    random.seed(1234)
    np.random.seed(1234)
    tf.random.set_seed(1234)


    # cassandra_url = "localhost"
    # cassandra_port = 9042
    # cassanra_user = "cassandra"
    # cassandra_password = "cassandra"
    # cassandra_keyspace = "zenprice"
    # cassandra_src_table = "pickle_data"
    # cassandra_dst_table = "pickle_values"
    # product_model = "samgung Galaxy A51 128GB"
    # product_id = 93
    # product_sub = "unlocked"
    # company = "Abcdin"
    # country = "CL"
    # pushgateway_url = "pushgateway-svc"
    # pushgateway_port = 9091

    # get environment variables
    cassandra_url = os.getenv("CASSANDRA_URL")
    cassandra_port = os.getenv("CASSANDRA_PORT")
    cassandra_user = os.getenv("CASSANDRA_USER")
    cassandra_passsword = os.getenv("CASSANDRA_PASSWORD")
    cassandra_keyspace = os.getenv("CASSANDRA_KEYSPACE")
    cassandra_src_table = os.getenv("CASSANDRA_SRC_TABLE")
    cassandra_dst_table = os.getenv("CASSANDRA_DST_TABLE")
    product_model = os.getenv("PRODUCT_MODEL")
    product_id = os.getenv("PRODUCT_ID")
    product_sub = os.getenv("PRODUCT_SUB")
    company = os.getenv("COMPANY")
    country = os.getenv("COUNTRY")
    pushgateway_url = os.getenv("PUSHGATEWAY_URL")
    pushgateway_port = os.getenv("PUSHGATEWAY_PORT")


    # prepare to collect metrics
    registry = CollectorRegistry()
    duration = Gauge(f'predicter_{product_id}_{product_model.replace(" ", "_").lower()}_{company.lower()}_{country.lower()}_duration_seconds',
        'Duration of batch job', registry=registry)
    measure_quant = Gauge(f'predicter_{product_id}_{product_model.replace(" ", "_").lower()}_{company.lower()}_{country.lower()}_measure_quant',
        'Amount of measures for predicting', registry=registry)


    # start metric collection
    try:
        with duration.time():

            # connect to cassandra
            logging.info(f"CONNECTING TO CASSANDRA KEYSPACE '{cassandra_keyspace}' at {cassandra_url}:{cassandra_port}...")
            auth_provider = PlainTextAuthProvider(username='cassandra', password='cassandra')
            policy = DCAwareRoundRobinPolicy(local_dc="dc1")
            cluster = Cluster([cassandra_url], port=int(cassandra_port), auth_provider=auth_provider)
            session = cluster.connect(cassandra_keyspace)
            logging.info(f"CONNECTION TO KEYSPACE ESTABLISHED.")

            # query data
            query = f"SELECT id, \
                        product_id, \
                        timestamp, \
                        model, \
                        country, \
                        company, \
                        subscription, \
                        price \
                        FROM {cassandra_keyspace}.pickle_data \
                        WHERE model = '{product_model}' \
                        AND product_id = {product_id} \
                        AND company = '{company}' \
                        AND subscription = '{product_sub}' \
                        AND country = '{country}' \
                        ALLOW FILTERING;" 
            statement = SimpleStatement(query, fetch_size=1000)
            prepared = session.prepare(query, keyspace=cassandra_keyspace)

            logging.info("QUERYING FOR DATA...")
            data = []
            for rows in session.execute(statement):
                data.append(rows)

            measure_quant.set(len(data))

            colnames = ["id", "product_id", "timestamp", "model", "country", "company", "subscription", "price"]
            data = pd.DataFrame(data, columns=colnames)


            # reorganize data
            logging.info("REORGANIZING DATA")
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
            raw_data = reorg[company]

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


            # create, fit, and predict
            logging.info("CREATING MODEL")
            model = LSTMSimple(n_steps=7, n_features=1)

            logging.info("FITTING MODEL...")
            model.fit(data_x=fit[0],
                            data_y=fit[1],
                            validation_data=test,
                            epochs=100,
                            batch_size=72,
                            verbose=1,
                            shuffle=False)

            logging.info("PREDICTING RESULTS...")
            results = model.predict(test[0])
            logging.info("PREDICT COMPLETED!!!")

            # store data to cassandra
            logging.info("CHECKING IF TABLE EXISTS...")
            rows = session.execute("SELECT table_name FROM system_schema.tables;")
            flag = False
            for row in rows:
                if cassandra_dst_table in row:      # table already exists
                    flag = True
            
            if flag is False:                       # table does not exist
                logging.info("TABLE DOES NOT EXIST.\nCREATING TABLE...")
                session.execute(f"CREATE TABLE {cassandra_dst_table} \
                                (product_id int PRIMARY KEY, \
                                timestamp timestamp, \
                                model varchar, \
                                country varchar, \
                                company varchar, \
                                subscription varchar, \
                                prediction list<float>);")
                logging.info("TABLE CREATED.")

            logging.info("WRITING DATA TO TABLE...")
            timestamp = datetime.now()  #.strftime(r"%d-%m-%Y %H:%M:%S.")
            session.execute(f"INSERT INTO {cassandra_dst_table} (product_id, timestamp, model, country, company, subscription, prediction) \
                            VALUES ({product_id}, '{timestamp}', '{product_model}', '{country}', '{company}', '{product_sub}', {[item for sublist in results for item in sublist]})")
                
            logging.info("WRINTING COMPLETED.")

            session.shutdown()
            cluster.shutdown()

    except:
        pass
    
    else:
        last_success = Gauge('mybatchjob_last_success', 
        'Unixtime my batch job last succeeded', registry=registry)
        last_success.set_to_current_time()

    finally:
        pushadd_to_gateway(f'{pushgateway_url}:{pushgateway_port}', job=f'predicter_predicter_{product_id}_{product_model.replace(" ", "_").lower()}_{company.lower()}_{country.lower()}', registry=registry)