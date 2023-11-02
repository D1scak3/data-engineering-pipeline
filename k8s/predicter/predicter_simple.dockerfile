# docker build -t d1scak3/predicter:lstm_simple -f predicter_simple.dockerfile .
# docker push d1scak3/predicter:lstm_simple
# docker image rm d1scak3/predicter:lstm_simple

FROM tensorflow/tensorflow:2.12.0

RUN mkdir app

WORKDIR /app

COPY requirements.txt requirements.txt

COPY lstm_simple.py lstm_simple.py

COPY predicter_simple.py predicter.py

ENV CASSANDRA_URL "cassandra-svc"
ENV CASSANDRA_USER "cassandra"
ENV CASSANDRA_PASSWORD "cassandra"
ENV CASSANDRA_KEYSPACE "keyspace"
ENV CASSANDRA_SRC_TABLE "src_table"
ENV CASSANDRA_DST_TABLE "dst_table"
ENV PRODUCT_MODEL "samgung Galaxy A51 128GB"
ENV PRODUCT_ID 93
ENV PRODUCT_SUB "unlocked"
ENV COMPANY "Abcdin"
ENV COUNTRY "CL"
ENV PUSHGATEWAY_URL "pushgateway-svc"
ENV PUSHGATEWAY_PORT 9091
ENV INSTANCE_LOG_ID "X"

RUN apt-get update && apt-get upgrade -y

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

CMD [ "python3", "predicter.py" ]