# Kubernetes pipeline deployment

## WARNING

The Kubernetes cluster might be heavier on the memory usage.
For an ideal environment, consider at least starting with 8Gb of ram.
Every command with any kind of path in it considers the root directory as **"k8s"**.

## Pre-deployment setup

- create minikube cluster and activate plugins (MetalLB, Metrics-Server) <!--, Ingress)-->

```bash
# create cluster
minikube start --cpus='8' --memory='8192'
minikube start --cpus='8' --memory='10240'

# enable addons
minikube addons enable metrics-server
minikube addons enable metallb
minikube ip # get the ip for MetalLB port range
minikube addons configure metallb # define port range based on ip


# create multi node cluster
minikube start --cpus='8' --memory='10240' --nodes='2'
minikube addons disable storage-provisioner
minikube addons disable default-storageclass
minikube addons enable volumesnapshots
minikube addons enable csi-hostpath-driver
kubectl patch storageclass csi-hostpath-sc -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'

```

- create custom docker images (cassandra, importer, predicter) and creata storage class (Rancher's local-path-storage)

```bash
# create and push cassandra
docker build -t d1scak3/cassandra:5.0 -f cassandra.dockerfile .
docker push d1scak3/cassandra:5.0

# create and push importer
docker build -f importer.dockerfile  -t d1scak3/importer:1.0 .
docker push d1scak3/importer:1.0

# create and push predicter
docker build -f predicter.dockerfile -t d1scak3/predicter:1.0 .
docker push d1scak3/predicter:1.0
```

## Rancher local path storage

```bash
kubectl apply -f provisioner/rancher/local-path-storage.yaml
kubectl apply -f provisioner/aws
```

## Strimzi deployment

- create namespace, configure strimzi to oversee namespace, and deploy cluster w/ metrics

```bash
# create namesapce
kubectl create namespace strimzi-system

# configure strimzi to overview namespace
sed -i 's/namespace: .*/namespace: strimzi-system/' strimzi/operator/*RoleBinding*.yaml

# deploy operator
kubectl apply -f strimzi/operator -n strimzi-system

# deploy cluster
kubectl apply -f strimzi/cluster.yaml -n strimzi-system
```

## Cassandra deployment

- create a namespace and deploy cassandra to kubernetes

```bash
kubectl create namespace cassandra
kubectl apply -f cassandra/cassandra.yaml -n cassandra
```

## Stargate deployment

- deploy coordinator and graphql api to kubernetes

```bash
kubectl apply -f stargate -n cassandra
```

## Python Cronjobs deployment

- create a namespace and deploy cronjobs

```bash
kubectl create namespace zenprice
kubectl apply -f importer/cron-importer.yaml -n cassandra
kubectl apply -f predicter/cron-predicter.yaml -n zenprice
```

## Monitoring

- deploy kubestate cluster role and deployment for cluster metrics

```bash
kubectl apply -f kubestate/ -n kube-system
```

- create monitoring namespace and deploy prometheus, prometheus pushgateway, and grafana

```bash
kubectl create namespace monitoring
kubectl apply -f monitoring -n monitoring
```

- credentials for grafana are

```txt
username: admin
password: admin
```

## Post-deployment setup

- create kafka topic through operator

```bash
kubectl apply -f strimzi/kafka-topic.yaml -n strimzi-system
```

- create cicd roll for ec2 continuous deployment

```bash
kubectl apply -f cicd/ -n zenprice
```

- port-forward cassandra service and create cassandra keyspace and table

```bash
kubectl port-forward service/cassandra 9042:9042
python3 src/cassandra/db_init.py -i localhost -p 9042 -k zenprice -t pickle_data
```

- send data to kafka through one of the available **load-balancer** type services

```bash
python3 src/exporter/manual-exporter.py -c exporter_conf.ini -t pickle_data -f long_product_group_id_23
```

- create token and populate graphql api with it

```bash
curl -L -X POST 'http://localhost:8081/v1/auth' \
  -H 'Content-Type: application/json' \
  --data-raw '{
    "username": "cassandra",
    "password": "cassandra"
}'
```

- query for data by accessing <http://192.168.67.10:8080/playground>
