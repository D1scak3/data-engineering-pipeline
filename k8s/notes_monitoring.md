# Monitoring

## Prometheus & Grafana
Prometheus and Grafana is a combination of free and open-source tools
that will provide the necessary utilities for monitoring, and possibly alerting as well.

While Prometheus is responsible for scraping metrics from several endpoints, Grafana will provide additional operations on top of the collected metrics in order to transform the data into information.

Alerting can be done by both components, however, it was not implemented.

IMPORTANT RESOURCES:
- https://sematext.com/blog/kubernetes-monitoring-tools/
- https://devopscube.com/setup-prometheus-monitoring-on-kubernetes/
- https://devopscube.com/setup-grafana-kubernetes/


## Strimzi (Kafka)
Strimzi already provides an endpoint for metric scraping by Prometheus.

The default configuration for metric exporting and dashboards were used.

IMPORTANT RESOURCES:
- https://strimzi.io/docs/operators/latest/deploying.html#assembly-metrics-str
- https://blog.devgenius.io/kafka-on-kubernetes-using-strimzi-part-6-monitoring-709a43198bf5
- https://github.com/danielqsj/kafka_exporter
- https://github.com/prometheus/jmx_exporter


## Cassandra
Cassandra does not export metrics compatible with prometheus by default.

Due to this aspect, we had to use the jmx exporter which is compatible with Prometheus.
A new image was created, copying the exporter and its configuration inside it.

IMPORTANT RESOURCES:
- https://www.cloudwalker.io/2020/05/17/monitoring-cassandra-with-prometheus/
- https://github.com/prometheus/jmx_exporter
- https://grafana.com/grafana/dashboards/12086-cassandra-dashboard/


## Python & Pushgateway
Prometheus assumes metrics are always present and ready to be scraped. This goes agains the nature of cronjobs, which are ephemeral and difficult monitoring.

Due to this important aspect a new component was needed. The Prometheus Pushgateway enables to store metrics taht are pushed from epehemeral jobs and aggregates them all in a sigle space where Prometheus can then proceed to scrape.

Metrics were created using the Prometheus client library. At the moment, only the duration of the task is being monitored, leaving space for further improvement.

IMPORTANT RESOURCES:
- https://www.groundcover.com/blog/kubernetes-job-scheduler
- https://www.robustperception.io/monitoring-batch-jobs-in-python/
- https://github.com/prometheus/client_python
- https://medium.com/@tristan_96324/prometheus-k8s-cronjob-alerts-94bee7b90511
- https://github.com/prometheus/pushgateway

## cAdvisor & Kubestate
Monitoring of the cluster itself is also important, namely resources, components, and performance.

This is possible with cAdvisor, for container monitoring, and kubestate, for cluster monitoring.

While cAdvisor is already part of kubernetes itself, it is a part of the kubelet component, Kubestate needs to be deployed.

IMPORTANT RESOURCES:
- https://sematext.com/blog/kubernetes-monitoring-tools/ (repeated on "prometheus & grafana")
- https://www.cloudforecast.io/blog/cadvisor-and-kubernetes-monitoring-guide/#cadvisor-overview
- https://github.com/kubernetes/kube-state-metrics/tree/main/examples/standard
- https://devopscube.com/setup-kube-state-metrics/