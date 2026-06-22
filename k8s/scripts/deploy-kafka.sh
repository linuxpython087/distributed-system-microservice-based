#!/bin/bash

set -e

NAMESPACE=messaging
RELEASE=kafka
CHART=./helm/kafka

echo "=============================="
echo "3. Clean stuck resources (optional safety)"
echo "=============================="

kubectl delete pods -n $NAMESPACE --all || true
kubectl delete statefulset -n $NAMESPACE --all || true
kubectl delete svc --all -n messaging || true

kubectl delete job -n $NAMESPACE --all || true

kubectl delete cm -n $NAMESPACE --all || true

kubectl delete deploy -n $NAMESPACE --all || true
echo "=============================="
echo "4. Install Kafka via Helm (step-by-step)"
echo "=============================="

kubectl apply -f ./helm/kafka/templates/01-configmap.yaml
sleep 10

kubectl apply -f ./helm/kafka/templates/02-headless-service.yaml
sleep 10

kubectl apply -f ./helm/kafka/templates/03-statefulset.yaml
sleep 10

kubectl apply -f ./helm/kafka/templates/04-service.yaml
sleep 10

kubectl apply -f ./helm/kafka/templates/07-configmap.yml
sleep 10

kubectl apply -f ./helm/kafka/templates/08-create-topic-job.yaml
sleep 10

kubectl apply -f ./helm/kafka/templates/09-deployment.yaml
sleep 10

echo "==========================="
echo "Kafka manifests applied"
echo "==========================="