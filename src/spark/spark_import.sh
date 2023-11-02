#!/bin/bash
# Do not set in cluster modes.
export PYSPARK_DRIVER_PYTHON=python
export PYSPARK_PYTHON=../../env/bin/python

spark-submit --master spark://localhost:7077 \
--archives pyspark_venv.tar.gz#environment \
db_import.py \
-t pickle_data \
-i 127.0.0.1 \
-p 29092 \
-k zenprice \
-g g1
-n zenprice_values

# spark-submit --master spark://localhost:7077/ \
# --archives pyspark_venv.tar.gz#environment \
# db_import.py \
# -t pickle_data \
# -i strimzi-system.my-cluster-kafka-external-bootstrap.svc.cluster.local \
# -p 9095 \
# -k zenprice \
# -n pickle_data \
# -g g1

# spark-submit --master k8s://https://192.168.67.2:8443 \
# --deploy-mode cluster \
# --conf spark.executor.instances=1 \
# --conf spark.kubernetes.container.image=apache/spark-py:v3.3.2 \
# --conf spark.kubernetes.file.upload.path='local:///opt/spark/tmp' \
# --archives pyspark_venv.tar.gz#environment \
# db_import.py \
# -t pickle_data \
# -i 127.0.0.1 \
# -p 29092 \
# -k zenprice \
# -n pickle_data \
# -g g2