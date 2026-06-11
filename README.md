 <div align="center">

# Ship It

### From Code to Kubernetes in One Git Push.

*A complete, production-grade DevOps pipeline — built entirely on your laptop, zero cloud cost.*

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1.0-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Kind-326CE5?style=flat-square&logo=kubernetes&logoColor=white)](https://kubernetes.io)
[![Terraform](https://img.shields.io/badge/OpenTofu-IaC-7B3FE4?style=flat-square&logo=opentofu&logoColor=white)](https://opentofu.org)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI%2FCD-2088FF?style=flat-square&logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![Prometheus](https://img.shields.io/badge/Prometheus-Monitoring-E6522C?style=flat-square&logo=prometheus&logoColor=white)](https://prometheus.io)
[![Grafana](https://img.shields.io/badge/Grafana-Dashboards-F46800?style=flat-square&logo=grafana&logoColor=white)](https://grafana.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

---

**[Overview](#-overview) · [Architecture](#-architecture) · [Prerequisites](#-prerequisites) · [Quick Start](#-quick-start) · [Project Structure](#-project-structure) · [Phases](#-phases) · [Demo Guide](#-demo-guide) · [Troubleshooting](#-troubleshooting)**

</div>

---

## 📖 Overview

**Ship It** is a hands-on DevOps project that demonstrates a complete, production-grade software delivery pipeline from a developer's first commit to a live, monitored Kubernetes deployment — **in under 60 seconds, on your laptop, for $0**.

Every tool and pattern used here mirrors what engineering teams at companies like Amazon, Google, and Netflix use in production. The only difference is that instead of running in the cloud, everything runs locally using Kind (Kubernetes in Docker).

### What happens when you run `git push`?

```
git push origin main
      │
      ▼
┌─────────────────────────────────────────┐
│         GitHub Actions Pipeline          │
│                                          │
│  ① pytest        (~10s)  ✅ or ❌ STOP  │
│  ② docker build  (~15s)                 │
│  ③ push to GHCR  (~10s)                 │
│  ④ kubectl apply  (~4s)                 │
└──────────────────┬──────────────────────┘
                   │
                   ▼
      ┌────────────────────────┐
      │   Kubernetes (Kind)    │
      │                        │
      │  Rolling update        │
      │  Zero downtime         │
      │  HPA auto-scaling      │
      └───────────┬────────────┘
                  │
                  ▼
      ┌────────────────────────┐
      │  Prometheus + Grafana  │
      │                        │
      │  Live metrics          │
      │  Request rate          │
      │  p95 latency           │
      └────────────────────────┘

Total: ~49 seconds end-to-end
```

### Why build this?

| Problem | Ship It Solution |
|---------|-----------------|
| "It works on my machine" | Docker image runs identically everywhere |
| Manual deployments break things | GitHub Actions pipeline with automated tests |
| No visibility into production | Prometheus + Grafana live dashboard |
| Infrastructure drift | OpenTofu IaC — everything in Git |
| Traffic spikes cause outages | HPA auto-scales pods automatically |

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Developer Workflow                        │
│                                                                  │
│   Edit Code  →  Test Locally  →  git commit  →  git push        │
└─────────────────────────────┬───────────────────────────────────┘
                              │ webhook trigger
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    GitHub Actions (Free Tier)                    │
│                                                                  │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────────────┐   │
│  │  pytest  │───▶│ docker build │───▶│    kubectl apply     │   │
│  │  7 tests │    │  + push GHCR │    │  (rolling update)    │   │
│  └──────────┘    └──────────────┘    └──────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              Kubernetes Cluster (Kind — 3 nodes)                 │
│                                                                  │
│  Namespace: ship-it  (managed by OpenTofu)                       │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    Deployment                            │    │
│  │                                                          │    │
│  │   ┌──────────────┐      ┌──────────────┐                │    │
│  │   │     Pod 1    │      │     Pod 2    │  ← HPA: 2-5    │    │
│  │   │  Flask App   │      │  Flask App   │    replicas    │    │
│  │   │  Port 5000   │      │  Port 5000   │                │    │
│  │   └──────┬───────┘      └──────┬───────┘                │    │
│  └──────────┼────────────────────┼────────────────────────┘    │
│             │                    │                               │
│  ┌──────────▼────────────────────▼────────────────────────┐    │
│  │              Service (ClusterIP: 80 → 5000)             │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌──────────────────────┐  ┌──────────────────────────────┐     │
│  │   ResourceQuota      │  │        LimitRange             │     │
│  │   CPU:  500m max     │  │   Default: 100m CPU / 64Mi    │     │
│  │   RAM:  256Mi max    │  │   Limit:   200m CPU / 128Mi   │     │
│  │   Pods: 10 max       │  │                               │     │
│  └──────────────────────┘  └──────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ /metrics scrape every 5s
┌─────────────────────────────────────────────────────────────────┐
│                   Observability Stack                            │
│                                                                  │
│   Prometheus ──────────────────────────▶ Grafana Dashboard      │
│   (time series DB)                       (live visualization)   │
│                                                                  │
│   Metrics: app_requests_total, app_request_latency_seconds       │
│   Panels:  Request rate · p95 Latency · Pod count               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📋 Prerequisites

Everything is **free and local** — no cloud account required.

### Required Tools

| Tool | Version | Purpose | Install |
|------|---------|---------|---------|
| Docker Desktop | Latest | Container runtime | [docker.com](https://docker.com/products/docker-desktop) |
| kubectl | v1.36+ | Kubernetes CLI | Pre-installed with Docker Desktop |
| Kind | v0.23+ | Local K8s cluster | [kind.sigs.k8s.io](https://kind.sigs.k8s.io) |
| Helm | v3.21+ | K8s package manager | [helm.sh](https://helm.sh/docs/intro/install) |
| OpenTofu | v1.12+ | Infrastructure as Code | [opentofu.org](https://opentofu.org/docs/intro/install) |
| Python | 3.11+ | Application runtime | [python.org](https://python.org) |
| Git | Latest | Version control | [git-scm.com](https://git-scm.com) |

### WSL2 Setup (Windows users)

If you're on Windows, run everything inside WSL2 (Ubuntu recommended). Enable Docker Desktop's WSL2 integration:

1. Open Docker Desktop → Settings → Resources → WSL Integration
2. Toggle on your Ubuntu distro
3. Click Apply & Restart

Verify everything is working:
```bash
docker run hello-world && kubectl version --client && kind version && helm version && tofu version
```

### Verify your setup
```bash
echo "=== Docker ===" && docker --version
echo "=== kubectl ===" && kubectl version --client
echo "=== Kind ===" && kind version
echo "=== Helm ===" && helm version
echo "=== OpenTofu ===" && tofu version
echo "=== Python ===" && python3 --version
echo "=== Git ===" && git --version
```

---

## ⚡ Quick Start

Clone and run the entire stack in 5 commands:

```bash
# 1. Clone the repo
git clone https://github.com/manishsinghkuswaha/Ship-it-end-to-end.git
cd Ship-it-end-to-end

# 2. Create the Kind cluster
kind create cluster --config kind-config.yaml

# 3. Provision infrastructure with OpenTofu
cd terraform && tofu init && tofu apply -auto-approve && cd ..

# 4. Build and load the Docker image
docker build -t ship-it:local . && kind load docker-image ship-it:local --name ship-it

# 5. Deploy everything
kubectl apply -f k8s/
```

Access the app:
```bash
kubectl port-forward svc/ship-it -n ship-it 5000:80
curl http://localhost:5000/
```

---

## 📁 Project Structure

```
ship-it/
│
├── app/                          # Flask application
│   ├── main.py                   # App + Prometheus metrics + 4 routes
│   ├── requirements.txt          # Python dependencies
│   └── test_main.py              # 7 pytest tests
│
├── k8s/                          # Kubernetes manifests
│   ├── deployment.yaml           # 2 replicas, rolling update strategy
│   ├── service.yaml              # ClusterIP service (port 80 → 5000)
│   ├── ingress.yaml              # NGINX ingress controller
│   ├── hpa.yaml                  # HPA: 2-5 pods on CPU > 50%
│   └── servicemonitor.yaml       # Prometheus ServiceMonitor
│
├── terraform/                    # Infrastructure as Code
│   ├── main.tf                   # Namespace + ResourceQuota + LimitRange
│   └── variables.tf              # Configurable variables
│
├── .github/
│   └── workflows/
│       └── deploy.yml            # CI/CD: test → build → push → deploy
│
├── kind-config.yaml              # 3-node Kind cluster config
├── docker-compose.yml            # Local dev stack (app + prometheus + grafana)
├── prometheus.yml                # Prometheus scrape config
└── Dockerfile                    # Multi-stage optimised image
```

---

## 🔧 Phases

### Phase 1 — The Flask Application

The app is intentionally simple — a task tracker with 4 routes. What makes it production-grade is the **observability built in from line one**.

**Routes:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | App info (name, version, task count) |
| GET | `/tasks` | List all tasks |
| POST | `/tasks` | Create a task `{"title": "..."}` |
| DELETE | `/tasks/<id>` | Delete a task by ID |
| GET | `/healthz` | Health check endpoint |
| GET | `/metrics` | Prometheus metrics endpoint |

**Prometheus metrics exposed:**

```
app_requests_total{method, endpoint, status}     # Counter
app_request_latency_seconds{endpoint}            # Histogram (p50, p95, p99)
```

**Run tests locally:**
```bash
cd app
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest test_main.py -v
```

Expected output:
```
test_main.py::test_index                    PASSED
test_main.py::test_create_task              PASSED
test_main.py::test_get_tasks                PASSED
test_main.py::test_delete_task              PASSED
test_main.py::test_delete_missing_task      PASSED
test_main.py::test_create_task_missing_title PASSED
test_main.py::test_healthz                  PASSED
7 passed in 0.35s
```

---

### Phase 2 — Docker

The Dockerfile is optimised for **layer caching** — the single most impactful Docker performance technique.

```dockerfile
FROM python:3.11-slim          # 50MB vs 900MB full image

WORKDIR /app

# ✅ Copy requirements FIRST — this layer gets cached
# If requirements.txt hasn't changed, pip install is skipped
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Copy code AFTER — this layer only re-runs when code changes
COPY app/ .

EXPOSE 5000

# ✅ HTTP health check — Kubernetes uses this for traffic routing
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/healthz')"

CMD ["python3", "main.py"]
```

**Build and test:**
```bash
# Build (first time: ~60s, subsequent: ~3s due to layer cache)
docker build -t ship-it:local .

# Run locally
docker run -d -p 5000:5000 --name ship-it-test ship-it:local

# Test all endpoints
curl http://localhost:5000/
curl http://localhost:5000/tasks
curl -X POST http://localhost:5000/tasks -H "Content-Type: application/json" -d '{"title": "Deploy to K8s"}'
curl http://localhost:5000/metrics | head -20

# Cleanup
docker stop ship-it-test && docker rm ship-it-test
```

**Run full local stack (app + Prometheus + Grafana):**
```bash
docker compose up --build -d
```

| Service | URL | Credentials |
|---------|-----|-------------|
| Flask app | http://localhost:5000 | — |
| Prometheus | http://localhost:9090 | — |
| Grafana | http://localhost:3000 | admin / admin |

---

### Phase 3 — Infrastructure as Code (OpenTofu)

All Kubernetes infrastructure is defined as code. Nothing is clicked through a UI.

**What OpenTofu manages:**

| Resource | Purpose |
|----------|---------|
| `kubernetes_namespace` | Isolated namespace for the app |
| `kubernetes_resource_quota` | Hard limits: 500m CPU, 256Mi RAM, 10 pods max |
| `kubernetes_limit_range` | Default container limits if not specified |

**Create the Kind cluster:**
```bash
kind create cluster --config kind-config.yaml
```

The `kind-config.yaml` creates a 3-node cluster (1 control-plane + 2 workers) with port mappings for ingress:

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: ship-it
nodes:
  - role: control-plane
    extraPortMappings:
      - containerPort: 80
        hostPort: 8080
  - role: worker
  - role: worker
```

**Provision with OpenTofu:**
```bash
cd terraform

# Download Kubernetes provider
tofu init

# Preview what will be created — no changes yet
tofu plan

# Apply — creates namespace, quota, limitrange
tofu apply -auto-approve
```

Expected output:
```
Plan: 3 to add, 0 to change, 0 to destroy.
Apply complete! Resources: 3 added, 0 changed, 0 destroyed.
```

**Verify:**
```bash
kubectl get namespace ship-it
kubectl get resourcequota -n ship-it
kubectl get limitrange -n ship-it
```

---

### Phase 4 — Kubernetes

**Load the image into Kind** (Kind can't pull from local Docker daemon by default):
```bash
docker build -t ship-it:local .
kind load docker-image ship-it:local --name ship-it
```

**Apply all manifests:**
```bash
kubectl apply -f k8s/
```

**Watch pods come up:**
```bash
kubectl get pods -n ship-it -w
```

**Verify everything is running:**
```bash
kubectl get all -n ship-it
```

Expected output:
```
NAME                           READY   STATUS    RESTARTS   AGE
pod/ship-it-5857b58f7-bkb7z    1/1     Running   0          40s
pod/ship-it-5857b58f7-lfqqn    1/1     Running   0          40s

NAME              TYPE        CLUSTER-IP       PORT(S)   AGE
service/ship-it   ClusterIP   10.96.146.238    80/TCP    40s

NAME                      READY   UP-TO-DATE   AVAILABLE
deployment.apps/ship-it   2/2     2            2

NAME                                          MINPODS   MAXPODS   REPLICAS
horizontalpodautoscaler.autoscaling/ship-it   2         5         2
```

**Access the app:**
```bash
# Port-forward (works on all platforms including WSL2)
kubectl port-forward svc/ship-it -n ship-it 5000:80

# In a new terminal
curl http://localhost:5000/
curl http://localhost:5000/tasks
```

**Trigger a rolling update:**
```bash
# Watch pods in one terminal
kubectl get pods -n ship-it -w

# Trigger rollout in another terminal
kubectl rollout restart deployment/ship-it -n ship-it

# Watch new pods come up before old ones terminate
# maxUnavailable: 0 guarantees zero downtime
```

**Key manifest details:**

`k8s/deployment.yaml` — rolling update strategy:
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1          # One extra pod during update
    maxUnavailable: 0    # Never reduce below desired replica count
```

`k8s/hpa.yaml` — auto-scaling:
```yaml
spec:
  minReplicas: 2
  maxReplicas: 5
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 50    # Scale when CPU > 50%
```

---

### Phase 5 — Prometheus + Grafana

**Install the full observability stack via Helm:**
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set grafana.adminPassword=admin \
  --set prometheus.prometheusSpec.podMonitorSelectorNilUsesHelmValues=false \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false
```

**Apply the ServiceMonitor** (tells Prometheus to scrape our app):
```bash
kubectl apply -f k8s/servicemonitor.yaml
```

**Access Grafana:**
```bash
kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80
```

Open http://localhost:3000 — login with `admin / admin`

**Key PromQL queries for dashboards:**

```promql
# Request rate per endpoint (last 1 minute)
sum(rate(app_requests_total[1m])) by (endpoint)

# p95 latency per endpoint
histogram_quantile(0.95,
  sum(rate(app_request_latency_seconds_bucket[1m])) by (le, endpoint)
)

# Error rate (5xx responses)
sum(rate(app_requests_total{status=~"5.."}[1m]))

# Pod count in namespace
count(kube_pod_info{namespace="ship-it"})
```

**Generate load to see live metrics:**
```bash
for i in {1..100}; do
  curl -s http://localhost:5000/ > /dev/null
  curl -s http://localhost:5000/tasks > /dev/null
  curl -s -X POST http://localhost:5000/tasks \
    -H "Content-Type: application/json" \
    -d "{\"title\": \"Task $i\"}" > /dev/null
  sleep 0.2
done
```

---

### Phase 6 — GitHub Actions CI/CD

The pipeline lives in `.github/workflows/deploy.yml` and runs on every push to `main`.

**Pipeline stages:**

```
git push origin main
        │
        ▼
┌───────────────┐     ┌─────────────────┐     ┌───────────────────┐
│  1. Run Tests │────▶│ 2. Build & Push  │────▶│  3. Deploy        │
│               │     │                 │     │                   │
│  pytest -v    │     │  docker build   │     │  kubectl apply    │
│  7 tests      │     │  push to GHCR   │     │  rolling update   │
│  ~10s         │     │  SHA tag        │     │  ~4s              │
└───────────────┘     └─────────────────┘     └───────────────────┘
                                                      ↓
                                              ✅ New version live
                                                    ~49s total
```

> **Critical:** Each job only runs if the previous one succeeded. If tests fail, Docker never builds. If Docker fails, Kubernetes never deploys.

**The gatekeeper demo — trigger a pipeline failure:**
```bash
# Add a failing test
cat >> app/test_main.py << 'EOF'

def test_intentional_failure():
    assert 1 == 2, "This blocks the deploy"
EOF

git add app/test_main.py
git commit -m "bug: introduce a failing test"
git push origin main
```

Watch the Actions tab — Build and Deploy never run. The cluster keeps serving the last good version.

**Recovery:**
```bash
# Remove the bad test
sed -i '/def test_intentional_failure/,+2d' app/test_main.py

git add app/test_main.py
git commit -m "fix: remove failing test"
git push origin main
```

All 3 jobs go green. Total recovery: ~49 seconds.

---

## 🎮 Demo Guide

Step-by-step commands for a live session:

### Session startup (run 15 min before)
```bash
# 1. Verify cluster
kubectl get nodes

# 2. Verify pods
kubectl get pods -n ship-it

# 3. Port-forward app (Terminal 1 — keep running)
kubectl port-forward svc/ship-it -n ship-it 5000:80

# 4. Port-forward Grafana (Terminal 2 — keep running)
kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80

# 5. Verify app
curl http://localhost:5000/

# 6. Open browser tabs
#    - http://localhost:5000     (App)
#    - http://localhost:9090     (Prometheus)
#    - http://localhost:3000     (Grafana — admin/admin)
#    - GitHub Actions tab
```

### Generate traffic for Grafana demo
```bash
for i in {1..50}; do
  curl -s http://localhost:5000/ > /dev/null
  curl -s http://localhost:5000/tasks > /dev/null
  curl -s -X POST http://localhost:5000/tasks \
    -H "Content-Type: application/json" \
    -d "{\"title\": \"Task $i\"}" > /dev/null
  sleep 0.2
done
```

### Rolling update demo
```bash
# Watch pods in terminal
kubectl get pods -n ship-it -w

# Trigger update (in second terminal)
kubectl rollout restart deployment/ship-it -n ship-it
```

### HPA scale demo
```bash
# Watch HPA
kubectl get hpa -n ship-it -w

# Generate heavy load (in second terminal)
for i in {1..200}; do curl -s http://localhost:5000/ > /dev/null; done
```

---

## 🔧 Troubleshooting

### App not responding
```bash
# Restart port-forward
kubectl port-forward svc/ship-it -n ship-it 5000:80

# Check pod status
kubectl get pods -n ship-it
kubectl describe pod <pod-name> -n ship-it
```

### Pods in CrashLoopBackOff
```bash
# Check logs
kubectl logs -n ship-it -l app=ship-it --previous

# Force restart
kubectl rollout restart deployment/ship-it -n ship-it
```

### Image not found
```bash
# Rebuild and reload into Kind
docker build -t ship-it:local .
kind load docker-image ship-it:local --name ship-it
kubectl rollout restart deployment/ship-it -n ship-it
```

### Grafana not loading
```bash
kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80

# Get password if changed
kubectl get secret monitoring-grafana -n monitoring \
  -o jsonpath="{.data.admin-password}" | base64 --decode && echo
```

### HPA showing `<unknown>` for CPU
```bash
# Install metrics-server
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Patch for Kind's self-signed certs
kubectl patch deployment metrics-server -n kube-system \
  --type='json' \
  -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'
```

### Full nuclear reset
```bash
kind delete cluster --name ship-it
kind create cluster --config kind-config.yaml
docker build -t ship-it:local . && kind load docker-image ship-it:local --name ship-it
cd terraform && tofu apply -auto-approve && cd ..
kubectl apply -f k8s/
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace --set grafana.adminPassword=admin
kubectl apply -f k8s/servicemonitor.yaml
```

---

## 📊 Project Stats

| Metric | Value |
|--------|-------|
| Pipeline duration | ~49 seconds end-to-end |
| Test suite | 7 tests in 0.35s |
| Docker image size | ~180MB |
| Kubernetes nodes | 3 (1 control-plane + 2 workers) |
| Default pod replicas | 2 |
| Max pod replicas (HPA) | 5 |
| Cloud cost | **$0** |
| Tools used | 8 |

---

## 🗺 What to Learn Next

Once you've mastered this pipeline, these are the natural next steps:

| Topic | Tool | Why |
|-------|------|-----|
| GitOps | ArgoCD | Declarative deployments from Git — next evolution after GitHub Actions |
| Secret management | HashiCorp Vault | Don't put secrets in environment variables |
| Service mesh | Istio | mTLS, traffic splitting, canary deployments |
| Cloud Kubernetes | AWS EKS | Same patterns, production scale |
| Container security | Trivy | Scan images for CVEs in the pipeline |
| Log aggregation | Loki + Grafana | Complete observability: metrics + logs + traces |

---

## 🤝 About the Author

**Manish Singh Kuswaha**
DevOps Engineer III at Amazon · AWS Certified (DevOps Professional, Solutions Architect, Developer Associate) · HashiCorp Terraform Associate

Building production Kubernetes infrastructure, security automation, and platform engineering tooling. Active mentor to 100+ students through GeeksForGeeks covering AWS, Kubernetes, Docker, CI/CD, and observability.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=flat-square&logo=linkedin)](https://linkedin.com/in/manishsinghkuswaha)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=flat-square&logo=github)](https://github.com/manishsinghkuswaha)

---

## 📄 License

This project is open source under the [MIT License](LICENSE). Clone it, break it, rebuild it.

---

<div align="center">

*Built with ❤️ for the DevOps community*

**Star ⭐ this repo if it helped you understand DevOps end-to-end**

</div>
