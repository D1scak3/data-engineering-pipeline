# KUBERNETES NOTES
These file incorporates notes about the deployment attempt of spark-on-k8s-operator and k8ssandra operator.


## Strimzi
This operator allows for the deployment of kafka clusters (zookeeper + brokers) on a kubernetes environment.

Pros
    - ease of scalling clusters
    - mirror maker (bidirectional data replication, topic configuration synch, and offset tracking across cluster)
    - compatibility with confluent_kafka python libraries
    - additional features (cluster operator, entity operator, topic operator, user operator), can be installed 

Cons
    - data replication between clusters is only done between 2 clusters (might become harder to replicate data across more clusters)


## spark-on-k8s-operator
This operator allows for the deployment of spark clusters (driver + workers) on a kubernetes environment.

Pros
    - interaction with the cluster is all made through yaml files
    - it allows for multiple and isolated spark clusters to be spawned on the same k8s cluster
    - same performance as baremetal/docker

Cons
    - interaction with the cluster is only through yaml files
    - new tasks need a new spark image with the task copied to the image
    - after a task is completed, the cluster is deleted (no real scalling is made)


## K8ssandra
This operator allows for the deployment of cassandra cluster, 
with some additional tools to help manage the clusters.

Pros
    - k8ssandra-operator is composed of cass-operator, reaper, medusa, stargate, and metric collector
    - cassandra cluster can be deployed over multiple k8s clusters and/or nodes
    - has built-in security with certificates

Cons
    - has no support (does not work?) for single cluster single node deployments
    - documentation is weak/incomplete (need to search forums/github issues for help)
    - no resource configuration help

Problems when deploying
    - no available cpu
    - readiness probe 500

It complains in general because of lack of resources/connection issues. 
No github issue, forum question, or stackoverflow question had anything related to this.

## Python Importer
The importer is responsible for importing data from a provided kafka topic into
a designated cassandra keyspace and table.

Data schema on cassandra is pre-defined.

Any future alterations will need to be made into the code, generate a new image, and then deploy it to the cluster.

## Python Predicter
```
export CASSANDRA_URL=localhost
export CASSANDRA_PORT=9042
export CASSANDRA_USER=cassandra
export CASSANDRA_PASSWORD=cassandra
export CASSANDRA_KEYSPACE=zenprice
export CASSANDRA_SRC_TABLE=pickle_data
export CASSANDRA_DST_TABLE=pickle_values
export PRODUCT_MODEL="samsung Galaxy A51 128GB"
export PRODUCT_ID=93
export PRODUCT_SUB=unlocked
export COMPANY=Abcdin
export COUNTRY=CL
```