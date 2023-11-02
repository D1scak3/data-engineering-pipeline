# builder step used to download and configure spark environment
FROM openjdk:11.0.11-jre-slim-buster as builder

# Add Dependencies for PySpark
RUN apt update && apt install -y curl wget software-properties-common ssh net-tools ca-certificates python3 python3-pip python3-numpy python3-matplotlib python3-scipy python3-pandas python3-simpy

RUN update-alternatives --install "/usr/bin/python" "python" "$(which python3)" 1

# Fix the value of PYTHONHASHSEED
# Note: this is needed when you use Python 3.3 or greater
ENV SPARK_VERSION=3.3.1
ENV HADOOP_VERSION=3
ENV SPARK_HOME=/opt/spark
ENV PYTHONHASHSEED=1

# copy spark to inside the container
COPY ../src/spark/spark-3.3.1-bin-hadoop3.tgz /apache-spark.tgz

# uncompress spark
RUN mkdir -p /opt/spark \
&& tar -xf apache-spark.tgz -C /opt/spark --strip-components=1 \
&& rm apache-spark.tgz

# Download and uncompress spark from the apache archive
# RUN wget -O apache-spark.tgz "https://dlcdn.apache.org/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}}-bin-hadoop${HADOOP_VERSION}.tgz" \
# && mkdir -p /opt/spark \
# && tar -xf apache-spark.tgz -C /opt/spark --strip-components=1 \
# && rm apache-spark.tgz


# Apache spark environment
FROM builder as apache-spark

WORKDIR /opt/spark

ENV SPARK_MASTER_PORT=7077 \
SPARK_MASTER_WEBUI_PORT=8080 \
SPARK_LOG_DIR=/opt/spark/logs \
SPARK_MASTER_LOG=/opt/spark/logs/spark-master.out \
SPARK_WORKER_LOG=/opt/spark/logs/spark-worker.out \
SPARK_WORKER_WEBUI_PORT=8080 \
SPARK_WORKER_PORT=7000 \
SPARK_MASTER="spark://spark-master:7077" \
SPARK_WORKLOAD="master"

EXPOSE 8080 7077 6066

RUN mkdir -p $SPARK_LOG_DIR && \
touch $SPARK_MASTER_LOG && \
touch $SPARK_WORKER_LOG && \
ln -sf /dev/stdout $SPARK_MASTER_LOG && \
ln -sf /dev/stdout $SPARK_WORKER_LOG

COPY start-spark.sh /

CMD ["/bin/bash", "/start-spark.sh"]