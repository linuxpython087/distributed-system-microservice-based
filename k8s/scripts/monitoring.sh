#!/bin/bash
set -e

NAMESPACE=monitoring

echo "==========================="
echo "1. Create namespace"
echo "==========================="

kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

echo "==========================="
echo "2. Install Prometheus stack"
echo "==========================="

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
  -n $NAMESPACE \
  --create-namespace

echo "==========================="
echo "3. Install Loki"
echo "==========================="

helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

helm upgrade --install loki grafana/loki-stack \
  -n $NAMESPACE \
  -f ./k8s/platform/monitoring/loki-values.yaml

echo "==========================="
echo "4. Restart Loki pods (safe rollout)"
echo "==========================="

kubectl rollout restart daemonset -n $NAMESPACE || true
kubectl rollout restart deployment -n $NAMESPACE || true

echo "==========================="
echo "5. Get Grafana admin password"
echo "==========================="

kubectl get secret prometheus-grafana -n $NAMESPACE \
  -o jsonpath="{.data.admin-password}" | base64 -d

echo
echo "==========================="
echo "Monitoring stack deployed"
echo "==========================="