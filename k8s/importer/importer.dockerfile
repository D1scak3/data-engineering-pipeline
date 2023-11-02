# docker build -f importer.dockerfile  -t d1scak3/importer:3.0 .
# docker push d1scak3/importer:3.0
# docker image rm d1scak3/importer:1.0

FROM python:3.10-slim

RUN mkdir app

WORKDIR /app

COPY requirements.txt requirements.txt

COPY importer_m2.py importer.py

ENV KAFKA_URL "kafka-service"
ENV KAFKA_PORT 9092
ENV KAFKA_TOPIC "topic"
ENV KAFKA_CONSUMER_GROUP "consumer-group"
ENV MEASURE_BATCH_SIZE 1000
ENV CASSANDRA_URL "cassandra-service"
ENV CASSANDRA_USER "cassandra"
ENV CASSANDRA_PASSWORD "cassandra"
ENV CASSANDRA_KEYSPACE "keyspace"
ENV CASSANDRA_TABLE "table"
ENV PUSHGATEWAY_URL "pushgateway-svc"
ENV PUSHGATEWAY_PORT 9091
ENV INSTANCE_LOG_ID "X"

RUN apt-get update && apt-get upgrade -y

RUN apt-get install librdkafka-dev -y

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

RUN ulimit -s 16384

CMD [ "python3", "importer.py" ]