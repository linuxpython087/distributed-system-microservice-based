#!/bin/bash

set -e

echo "Create namespaces..."
kubectl apply -R -f k8s/bootstrap/namespaces/

echo "Deploy secret store..."
kubectl apply -R -f k8s/secrets/cluster-secret-store/

echo "Deploy namespace secrets..."
kubectl apply -R -f k8s/secrets/namespaces/

echo "Wait for secrets..."
sleep 20

echo "Deploy postgres..."
helm upgrade --install postgres helm/postgres -n database

echo "Deploy kafka..."
helm upgrade --install kafka helm/kafka -n messaging

echo "Deploy order-service..."
helm upgrade --install order-service helm/order_service -n order-service

echo "Done."