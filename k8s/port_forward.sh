#!/bin/bash

# kubectl port-forward svc/cassandra 9042:9042 -n cassandra &
# kubectl port-forward svc/pushgateway-svc 9091:9091 -n monitoring &
# kubectl port-forward svc/prometheus-svc 9090:9090 -n monitoring &
# kubectl port-forward svc/grafana-svc 3000:3000 -n monitoring &

# Function to clean up port forwarding
cleanup() {
  echo "Cleaning up port forwards..."
  kill $(jobs -p)  # Terminate all background jobs
  exit 0
}

# Set up a trap to catch Ctrl+C and run the cleanup function
trap cleanup INT

# Start port forwarding in the background
kubectl port-forward svc/cassandra 9042:9042 -n cassandra &
kubectl port-forward svc/pushgateway-svc 9091:9091 -n monitoring &
kubectl port-forward svc/prometheus-svc 9090:9090 -n monitoring &
kubectl port-forward svc/grafana-svc 3000:3000 -n monitoring &
kubectl port-forward svc/graphql-svc 8080:8080 -n cassandra &
kubectl port-forward svc/coordinator-svc 8081:8081 -n cassandra &

# Keep the script running
echo "Press Ctrl+C to stop port forwards..."
wait