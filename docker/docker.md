# Docker Image Tags

| Image 	| Zookeeper 	| Confluent Kafka 	| Bitnami Spark 	| Apache Cassandra 	|
|:-----:	|:---------:	|:---------------:	|:-------------:	|:----------------:	|
|  Tag  	|    3.8    	|      7.3.0      	|      3.3      	|       4.0      	|


# MINIKUBE
```
docker network create --subnet 192.168.9.0/24 --driver bridge minikube

minikube start --cpus='4' --kvm-gpu=true --network='minikube' --memory 4096
```

# DOCKER COMMANDS

## POSTGRES 
Run Postgres while mounting a directory into the container.
RUN FROM THE ROOT DIRECTORY OF THE REPOSITORY.
```
docker run --name postgres \
-e POSTGRES_PASSWORD=mysecretpassword \
--mount type=bind,source="$(pwd)/data/dump.psql",target=/home/data/dump.psql \
-p 5432:5432 \
-d postgres
```

Import dump
```
#helpful commands inside the container
psql -> enter postgres
\l # list databases
\d # list tables
\dt+ -> list tables with extra info

# main commands
su postgres -> change user
psql -d databasename -U username -f file.psql -> import dump
# db_name postgres
# username postgres
# database name is usually "zenprice"
```

Export to JSON
```
\copy (
    select json_agg(row_to_json(t)) :: text
    from (
         select rim_facts.id, prices.id, plans.id, prices.created_at, prices.updated_at, prices.value, prices.currency, plans.plan_type
         from rim_facts, prices, plans
         where rim_facts.plan_id = plans.id
         and rim_facts.price_id = prices.id
         ) t
) to '/tmp/json_data.json'
```

Then copy the file from the /tmp dir inside the container to the host machine. (ftp, vscode-docker plugin, etc...)


## BENTHOS
Create a config and run Benthos.
```
# create a config
docker run --rm jeffail/benthos create nats/protobuf/aws_sqs > ./benthos.yaml

# run benthos with config
docker run --rm -v $(pwd)/benthos.yaml:/benthos.yaml jeffail/benthos
```

## KAFKACAT
Send data from kafka
```
docker run -it --rm --network=smack \
        edenhill/kcat:1.7.1 \
                -b broker:9092 \
                -t test \
                -K: \
                -P <<EOF

1:{"order_id":1,"order_ts":1534772501276,"total_amount":10.50,"customer_name":"Bob Smith"}
2:{"order_id":2,"order_ts":1534772605276,"total_amount":3.32,"customer_name":"Sarah Black"}
3:{"order_id":3,"order_ts":1534772742276,"total_amount":21.00,"customer_name":"Emma Turner"}
EOF
```

Read data from kafka
```
docker run -it --rm --network=smack \
        edenhill/kcat1.7.1 \
           -b broker:9092 \
           -C \
           -f '\nKey (%K bytes): %k\t\nValue (%S bytes): %s\n\Partition: %p\tOffset: %o\n--\n' \
           -t test
```