#!/bin/bash

export KUBECONFIG=~/.kube/config

done

# importer cronjobs
export CRONJOB_NAMES=$(kubectl get cronjobs -n $AWS_DATA_ENG_IMP_NAMESPACE -o jsonpath='{.items[*].metadata.name}')

for CRONJOB_NAME in "$CRONJOB_NAMES"; do
  kubectl delete cronjob "$CRONJOB_NAME" -n "$AWS_DATA_ENG_IMP_NAMESPACE"
done

kubectl apply -f "$(pwd)"/k8s/importer/cron_importer.yaml -n "$AWS_DATA_ENG_IMP_NAMESPACE"

# predicter cronjobs
export CRONJOB_NAMES=$(kubectl get cronjobs -n $AWS_DATA_ENG_PRED_NAMESPACE -o jsonpath='{.items[*].metadata.name}')

for CRONJOB_NAME in "$CRONJOB_NAMES"; do
  kubectl delete cronjob "$CRONJOB_NAME" -n "$AWS_DATA_ENG_PRED_NAMESPACE"

kubectl apply -f "$(pwd)"/k8s/predicter/cron_predicter.yaml -n "$AWS_DATA_ENG_PRED_NAMESPACE"