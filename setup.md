# Steps for setting up the pipeline
- make sure cassandra.yml is copied into cassandra#.yml(s)
- docker-compose up and __WAIT UNTIL EVERYTHING IS UP__
- run db_init.py to create keyspace 
- run kafka_producer.py w/ getting_started.ini config to send values to kafka
- run submit.sh script to send python task to spark
- send curl to graphql api to generate auth token
- add token to header of requests to the graphql api


Curl for token generation
```
curl -L -X POST 'http://localhost:8081/v1/auth' \
  -H 'Content-Type: application/json' \
  --data-raw '{
    "username": "cassandra",
    "password": "cassandra"
}'
```