Voici un **README.md propre, structuré et professionnel (anglais)** basé sur tout ton travail (Loki + Promtail + Prometheus + Grafana + troubleshooting + SRE setup).


# Observability Stack (Loki + Prometheus + Grafana) on Kubernetes

This project sets up a full observability stack on Kubernetes using:

- **Loki** → Logs aggregation
- **Promtail** → Log shipping agent
- **Prometheus** → Metrics collection
- **Grafana** → Unified visualization (logs + metrics)



# 1. Prerequisites

- Kubernetes cluster (Minikube / K3s / Docker Desktop / cloud cluster)
- kubectl configured
- Helm installed



# 2. Add Helm Repositories

```bash
helm repo add grafana https://grafana.github.io/helm-charts

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts

helm repo update
````

---

# 3. Install Loki Stack (Logs)

## 3.1 Get default values

```bash
helm show values grafana/loki-stack > loki-values.yaml
```
```yaml
test_pod:
  enabled: true
  image: bats/bats:1.8.2
  pullPolicy: IfNotPresent

loki:
  enabled: true
  isDefault: true
  url: http://{{(include "loki.serviceName" .)}}:{{ .Values.loki.service.port }}
  readinessProbe:
    httpGet:
      path: /ready
      port: http-metrics
    initialDelaySeconds: 45
  livenessProbe:
    httpGet:
      path: /ready
      port: http-metrics
    initialDelaySeconds: 45
  datasource:
    jsonData: "{}"
    uid: ""


promtail:
  enabled: true
  config:
    logLevel: info
    serverPort: 3101
    clients:
      - url: http://{{ .Release.Name }}:3100/loki/api/v1/push

fluent-bit:
  enabled: false

grafana:
  enabled: false
  sidecar:
    datasources:
      label: ""
      labelValue: ""
      enabled: true
      maxLines: 1000
  image:
    tag: latest

prometheus:
  enabled: false
  isDefault: false
  url: http://{{ include "prometheus.fullname" .}}:{{ .Values.prometheus.server.service.servicePort }}{{ .Values.prometheus.server.prefixURL }}
  datasource:
    jsonData: "{}"

filebeat:
  enabled: false
  filebeatConfig:
    filebeat.yml: |
      # logging.level: debug
      filebeat.inputs:
      - type: container
        paths:
          - /var/log/containers/*.log
        processors:
        - add_kubernetes_metadata:
            host: ${NODE_NAME}
            matchers:
            - logs_path:
                logs_path: "/var/log/containers/"
      output.logstash:
        hosts: ["logstash-loki:5044"]

logstash:
  enabled: false
  image: grafana/logstash-output-loki
  imageTag: 1.0.1
  filters:
    main: |-
      filter {
        if [kubernetes] {
          mutate {
            add_field => {
              "container_name" => "%{[kubernetes][container][name]}"
              "namespace" => "%{[kubernetes][namespace]}"
              "pod" => "%{[kubernetes][pod][name]}"
            }
            replace => { "host" => "%{[kubernetes][node][name]}"}
          }
        }
        mutate {
          remove_field => ["tags"]
        }
      }
  outputs:
    main: |-
      output {
        loki {
          url => "http://loki:3100/loki/api/v1/push"
          #username => "test"
          #password => "test"
        }
        # stdout { codec => rubydebug }
      }

# proxy is currently only used by loki test pod
# Note: If http_proxy/https_proxy are set, then no_proxy should include the
# loki service name, so that tests are able to communicate with the loki
# service.
proxy:
  http_proxy: ""
  https_proxy: ""
  no_proxy: ""



```

## 3.2 Install Loki Stack

```bash
helm install loki grafana/loki-stack \
  --namespace monitoring \
  --create-namespace \
  -f loki-values.yaml
```

---

# 4. Promtail Configuration

Promtail is configured to:

* Read Kubernetes pod logs
* Parse JSON logs
* Extract structured fields (event, service, status_code, etc.)
* Send logs to Loki

## Example Promtail pipeline

```yaml
server:
  log_level: info
  log_format: logfmt
  http_listen_port: 3101
  

clients:
  - url: http://loki:3100/loki/api/v1/push

positions:
  filename: /run/promtail/positions.yaml

scrape_configs:
  # See also https://github.com/grafana/loki/blob/master/production/ksonnet/promtail/scrape_config.libsonnet for reference
  - job_name: kubernetes-pods

    pipeline_stages:
      - cri: {}

      - match:
          selector: '{app="order-service-api"}'
          stages:

            # Parse container wrapper
            - json:
                expressions:
                  log:

            # Replace current line with extracted JSON
            - output:
                source: log

            # Parse application JSON
            - json:
                expressions:
                  event:
                  service:
                  environment:
                  correlation_id:
                  status_code:
                  method:
                  duration_ms:
                  path:
                  level:
                  timestamp:
                  order_id:
                  user_id:
                  idempotency_key:

            # Promote useful fields to labels
            - labels:
                service:
                event:
                level:
                method:
                status_code:
 
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels:
          - __meta_kubernetes_pod_controller_name
        regex: ([0-9a-z-.]+?)(-[0-9a-f]{8,10})?
        action: replace
        target_label: __tmp_controller_name
      - source_labels:
          - __meta_kubernetes_pod_label_app_kubernetes_io_name
          - __meta_kubernetes_pod_label_app
          - __tmp_controller_name
          - __meta_kubernetes_pod_name
        regex: ^;*([^;]+)(;.*)?$
        action: replace
        target_label: app
      - source_labels:
          - __meta_kubernetes_pod_label_app_kubernetes_io_instance
          - __meta_kubernetes_pod_label_instance
        regex: ^;*([^;]+)(;.*)?$
        action: replace
        target_label: instance
      - source_labels:
          - __meta_kubernetes_pod_label_app_kubernetes_io_component
          - __meta_kubernetes_pod_label_component
        regex: ^;*([^;]+)(;.*)?$
        action: replace
        target_label: component
      - action: replace
        source_labels:
        - __meta_kubernetes_pod_node_name
        target_label: node_name
      - action: replace
        source_labels:
        - __meta_kubernetes_namespace
        target_label: namespace
      - action: replace
        replacement: $1
        separator: /
        source_labels:
        - namespace
        - app
        target_label: job
      - action: replace
        source_labels:
        - __meta_kubernetes_pod_name
        target_label: pod
      - action: replace
        source_labels:
        - __meta_kubernetes_pod_container_name
        target_label: container
      - action: replace
        replacement: /var/log/pods/*$1/*.log
        separator: /
        source_labels:
        - __meta_kubernetes_pod_uid
        - __meta_kubernetes_pod_container_name
        target_label: __path__
      - action: replace
        regex: true/(.*)
        replacement: /var/log/pods/*$1/*.log
        separator: /
        source_labels:
        - __meta_kubernetes_pod_annotationpresent_kubernetes_io_config_hash
        - __meta_kubernetes_pod_annotation_kubernetes_io_config_hash
        - __meta_kubernetes_pod_container_name
        target_label: __path__
  
  

limits_config:
  

tracing:
  enabled: false

```

## Reload Promtail Secret

```bash
kubectl delete secret loki-promtail -n monitoring
kubectl create secret generic loki-promtail \
  --from-file=./promtail.yaml \
  -n monitoring

kubectl delete pod -l app=promtail -n monitoring
```



# 5. Install Prometheus Stack (Metrics)

## 5.1 Install kube-prometheus-stack

```bash
helm install prometheus prometheus-community/kube-prometheus-stack \
  -n monitoring \
  --create-namespace
```


# 6. Grafana Access

## 6.1 Port-forward Grafana

```bash
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
```

Access:


http://localhost:3000
```

Default login:
in this part you need to check you local secret 

```bash
kubectl get secrets -n monitoring
kubectl desribe secret secret-name -n monitoring


kubectl get secret -n monitoring prometheus-grafana \
  -o jsonpath="{.data.admin-password}" | base64 -d
```



# 7. Add Data Sources in Grafana

## 7.1 Loki (Logs)

Go to:

```
Grafana → Connections → Data Sources → Loki
```

URL:

```
http://loki.monitoring.svc.cluster.local:3100
```

Test:

```bash
kubectl exec -it -n monitoring deploy/prometheus-grafana -- \
wget -qO- http://loki.monitoring.svc.cluster.local:3100/ready
```

Expected:

```
ready
```

---

## 7.2 Prometheus (Metrics)

Add data source:

```
URL:
http://prometheus-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090
```

Test inside Grafana pod:

```bash
wget -qO- http://prometheus-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090/-/ready
```

Expected:

```
Prometheus Server is Ready.
```

---

# 8. Common Issue Fixes

## Loki not reachable from Grafana UI

Problem:

* Loki reachable from pod shell
* NOT working in Grafana UI

Fix:

* Use **Kubernetes service DNS**
* Ensure same namespace access:

```
http://loki.monitoring.svc.cluster.local:3100
```

---

## Port conflict (Grafana)

If:

```
bind: address already in use
```

Fix:

```bash
kubectl port-forward -n monitoring svc/prometheus-grafana 3001:80
```

---

# 9. Architecture Overview

```
[ Applications ]
      ↓ logs
[ Promtail ]
      ↓
[ Loki ] ←────── Grafana (Logs UI)

[ Kubernetes Metrics ]
      ↓
[ Prometheus ] ←── Grafana (Metrics UI)

                ↓
            Unified Grafana Dashboard
```

---

# 10. SRE Final Result

You now have:

✔ Centralized logs (Loki)
✔ Cluster metrics (Prometheus)
✔ Unified visualization (Grafana)
✔ Kubernetes observability pipeline
✔ Structured JSON log parsing
✔ Label-based filtering (service, event, status_code)

---

# 11. Next Improvements

* Add Alertmanager alerts
* Create dashboards (latency, error rate, CPU)
* Add tracing (Tempo / OpenTelemetry)
* Add log correlation (trace_id linking)

```