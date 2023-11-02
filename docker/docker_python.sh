#!/bin/bash
docker run --rm -it --network=smack \
--mount type=bind,source="/home/miguel/mestrado/2_ano/thesis_smack/src/spark",target="/home/spark" \
python:3.10-slim /bin/bash
# -v /spark:/home/spark \