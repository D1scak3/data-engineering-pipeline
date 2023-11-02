# KUBERNETES RESEARCH
This file agglomerates every detail/info researched with the intent of providing the most dynamism to the whole pipeline.

## APPROACH
The original idea is to implement CI/CD through a GitOps approach. The cluster is meant to auto scale according to workload. 

The ideal scenario is for users to simply provide the model/data to the pipeline, and receive the predicted results.

## TOOLS
These components represent core functionlities of the pipeline. 
As such, a way to handle them ona kubernetes cluster is necessary. Operators are the first idea to scale these components accordingly to the workload.
- strimzi (apache kafka)
- spark-on-k8s-operator (apache spark)
- k8ssandra (apache cassandra w/ stargate api)

Some other components that could be used (based on chatgpt):
- for k8s:
  - kubeflow
  - tensorflow extended
  - seldon core
  - open data hub
  - mlflow
- for docker/compose:
  - docker machine learning kit (dmlt)
  - mlflow
  - tensorflow serving
  - hugging face transformers
  - nvidia gpu cloud

## CI/CD
These components are responsible for providing continous integration/deployment to the pipeline. They are meant to integrate well with Kubernetes and Git repositories.
- GitLab CI/CD
- Argo CD


# IMPORTANT COMMANDS/DETAILS

## Docker
```
docker network create --subnet 192.168.9.0/24 --driver bridge minikube
docker network create --driver bridge minikube
```

## Minikube
```
minikube start --cpus='4' --kvm-gpu=true --memory='4096' \
--nodes 2 -p zenprice

minikube start --cpus='8' --memory='8192'
```

```
minikube addons disable storage-provisioner -p zenprice
kubectl delete storageclass standard
kubectl create namespace 
kubectl apply -f provisioner/
```

```
minikube ip -p zenprice
minikube addons enable metallb -p zenprice
minikube addons condigure metallb -p zenprice
```

## STRIMZI
```
# create rbac's and evrything else
# make strimzi watch the specific namespace where it is installed <my-cluster-operator-namespace> in this case

sed -i 's/namespace: .*/namespace: strimzi-system/' install/cluster-operator/*RoleBinding*.yaml

kubectl create namespace strimzi-system

kubectl apply -f install/cluster-operator -n strimzi-system
```

```
# deploy kafka cluster
kubectl apply -f examples/kafka/kafka-ephemeral-single.yaml -n strimzi-system
kubectl apply -f examples/kafka/kafka-persistent.yaml -n strimzi-system
```

Important to note that default values only work with kafka-persistent version.
Ephemeral version does not work.
check: https://strimzi.io/docs/operators/latest/configuring.html#type-KafkaMirrorMaker2-reference
```
# if let be, it deploys topic and user operators with default values
# it shows as entity operators when getting all pods
kubectl apply -f examples/kafka/kafka-persistent.yaml -n strimzi-system
```

```
# deploy kafka mirror maker 2
# v1 is deprecated since kafka 3.0.0
# current kafka version (in use) is 3.4.0
# NEEDS CONFIGURATION
kubectl apply -f examples/mirror-maker/kafka-mirror-maker-2.yaml -n strimzi-system
```

## SPARK-ON-K8S-OPERATOR
```
helm install <cluster-name> spark-operator/spark-operator --namespace <operator-namespace> --set sparkJobNamespace=<cluster-namespace>
helm install zenprice spark-operator/spark-operator \
--namespace spark-operator \
--set webhook.enable=true \
--set serviceAccounts.spark.name=spark \
--set sparkJobNamespace="default"

```

```
kubectl apply -f spark-py-pi.yaml
```

## K8SSANDRA OPERATOR
This crap does not work...

```
helm repo add jetstack https://charts.jetstack.io

helm repo add k8ssandra https://helm.k8ssandra.io/stable

helm install cert-manager jetstack/cert-manager --namespace cert-manager --create-namespace --set installCRDs=true

helm install k8ssandra-operator k8ssandra/k8ssandra-operator -n k8ssandra-operator --create-namespace
```