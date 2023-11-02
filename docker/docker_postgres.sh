#!/bin/bash

docker run --name postgres \
-e POSTGRES_PASSWORD=mysecretpassword \
--mount type=bind,source="/home/miguel/mestrado/2_ano/thesis_smack/data/dump.psql",target=/home/data/dump.psql \
-p 5432:5432 \
--network minikube \
-d postgres \
&& \
sleep 1s \
&& \
docker exec postgres /bin/bash -c "su postgres && psql -d postgres -U postgres < /home/data/dump.psql"