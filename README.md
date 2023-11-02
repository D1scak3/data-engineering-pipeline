# Data Engineering Pipeline
This pipeline was made in the context of my master's degree dissertation.

The pipeline is an adaptation of the SMACK stack to a Kubernetes environment.

The pipeline is divided into 5 layers, each representing a layer of the data engineering lifecyle.
Along the components, these are:
- data generation (Python costum component)
- data ingestion (Strimzi operator for Apache Kafka)
- data storage layer (Apache Cassandra and Python costum component)
- data processing layer (Python costum component)
- data serving layer (Stargate Coordinator and Graphql API) 

The pipeline also has monitoring:
- Prometheus for metric collection
- Prometheus Pushgateway for metric aggregation of CronJobs
- Grafana for metric visualization

Storage is provided by Rancher's local path provisioner.

The cluster ideally will need of at least 8 CPUs and 10Gib of memory.
