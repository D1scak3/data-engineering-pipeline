# Docker PoC pipeline deployment

## WARNING

For the pipeline to work as intended, you might need 16Gb or RAM or more, depending on the way your OS handles memory caching and swapping.

Ensure python version of virtual environment is the same as the one present on Spark. It leads to some "interesting" headaches.

## Pre-deployment setup

-   create python virtual environment and install dependencies (**use python3.9**)

```
python3.9 -m venv env            # create env
source env/bin/activate           # activate env
pip install -r requiremetns.txt   # install requirements
```

-   create docker network

```
docker network create smack   # create the network
```

-   make sure **cassandra#.yaml** are in the same directory as the **docker.compose.yaml**

-   deploy pipeline through the **docker-compose.yml** file

```
docker compose -f docker/docker-compose.yaml up
```

-   wait for evey container to be up (besides kafka container responsible for creating the topics)

## Post-deployment setup

-   create access token for accessing graphql api w/ cassandra username and password (curl against stargate coordinator on port **8081**)

```
curl -L -X POST 'http://localhost:8081/v1/auth' \
  -H 'Content-Type: application/json' \
  --data-raw '{
    "username": "cassandra",
    "password": "cassandra"
}'
```

-   put token on graphql api (access http://localhost:8085/playground)

-   create keyspace on cassandra cluster with python script

```
cd src/cassandra
python3 db_init.py -i 127.0.0.0 -p 9042 -k zenprice
```

## Importing data into the pipeline

-   execute manual data importer (inputs data from a pickle file into kafka)
-   make sure the **exporter_conf.ini** file has the intended kafka IP (localhost:29092, since the connection is made from the host)

```
cd /src/postgres
python3 manual_exporter.py -c exporter_conf.ini -t pickle_data -f long_product_group_id_23
```

## Spark tasks in order of execution

-   create virtual environment pack to be submited to spark

```
cd src/spark
venv-pack -o pyspark_venv.tar.gz
```

-   change into **src/spark** directory
-   export enviroment variables to point to pyspark driver and python

```
export PYSPARK_DRIVER_PYTHON=python
export PYSPARK_PYTHON=../../env/bin/python
```

-   submit spark task for storing kafka data into cassandra (ip of kafka is localhost, since spark cant resolve dns)

```
spark-submit --master spark://localhost:7077/ \
--archives pyspark_venv.tar.gz#environment \
db_import.py \
-t pickle_data \
-i localhost \
-p 29092 \
-k zenprice \
-n pickle_data \
-g g1
```

-   submit spark task for processing data and storing it into a new cassandra table

```
spark-submit --master spark://localhost:7077 \
--archives pyspark_venv.tar.gz#environment \
delta_predict.py \
-m "samsung Galaxy A51 128GB" \
-p 93 \
-c Abcdin \
-q CL \
-k zenprice \
-s unlocked \
-n pickle_predictions
```

## Query for data through Graphql

-   access http://localhost:8085/playground
-   change to the **"graphql" tab** on the top right corner
-   change to the zenprice namespace in by changing the last "path" in the url to the keyspace name
-   run the following graphql query (results shows predictions and final prediction)

```
query tableValues{
	zenprice_values
  {
    values
    {
      id
      product_id
      price_id
      plan_id
      created_timestamp
      updated_timestamp
      currency
      brand
      model
      subscription
    }
  }
}

query tableValues{
	pickle_predictions
  {
    values
    {
      product_id
      timestamp
      model
      subscription
      prediction
    }
  }
}
```

-   the output of the query (last vlue is the prediction of the product)

```
{
  "data": {
    "pickle_predictions": {
      "values": [
        {
          "product_id": 93,
          "timestamp": "2023-06-05T17:44:48.487Z",
          "model": "samsung Galaxy A51 128GB",
          "subscription": "unlocked",
          "prediction": [
            191.23055,
            190.81834,
            190.40608,
            189.99385,
            189.58151,
            189.16916,
            188.75676,
            188.34431,
            187.93182,
            187.51927,
            187.10674,
            186.69414,
            186.47128,
            186.36096,
            186.2862,
            186.21718,
            186.12608,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766,
            186.08766
          ]
        }
      ]
    }
  }
}
```
