#!/bin/bash
docker run prom/prometheus:v2.43.0 \
-p 9090:9090 \
--network=minikube \
-v prometheus.yaml:/etc/prometheus/prometheus.yaml \
-v prometheus.rules:/etc/prometheus/prometheus.rules