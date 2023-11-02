#!/bin/bash
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