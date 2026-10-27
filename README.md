# End-to-End DevSecOps Microservices Deployment with GitOps (ArgoCD & Kubernetes)

[![DevSecOps CI/CD Pipeline](https://github.com/abhishek85607/devsecops-microservices/actions/workflows/devsecops.yml/badge.svg)](https://github.com/abhishek85607/devsecops-microservices/actions)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Kind-326CE5?logo=kubernetes&logoColor=white)](https://kubernetes.io/)
[![ArgoCD](https://img.shields.io/badge/GitOps-ArgoCD-EF7B4D?logo=argo&logoColor=white)](https://argoproj.github.io/cd/)
[![Docker](https://img.shields.io/badge/Docker-Buildx-2496ED?logo=docker&logoColor=white)](https://hub.docker.com/u/abhiraj328)
[![Security](https://img.shields.io/badge/Security-Trivy%20%7C%20Bandit-FF4F8B)](https://aquasecurity.github.io/trivy/)

A production-grade, enterprise-ready **4-tier microservices platform** deployed on a multi-node Kubernetes cluster. The project features an automated shift-left security CI/CD pipeline and automated GitOps continuous deployment using **ArgoCD**, ensuring zero-downtime rolling releases and cluster self-healing.

---

## 🏛 Architecture Overview

The system is deployed on a multi-node Kubernetes cluster running inside AWS EC2 infrastructure.

```text
[ Developer Commit / PR ]
           │
           ▼
┌────────────────────────────────────────────────────────┐
│               GitHub Actions CI Pipeline               │
│  ├─ Code Linting & Static Analysis (Flake8, Bandit)   │
│  ├─ Dependency Vulnerability Audit (NPM Audit)         │
│  ├─ Filesystem & Secret Scan (Trivy)                   │
│  ├─ Multi-arch Container Build (Docker Buildx)         │
│  ├─ Container Image Vulnerability Scan (Trivy)        │
│  └─ Push Hardened Images to Docker Hub Registry       │
└────────────────────────────────────────────────────────┘
           │
           ▼ (Auto-Commit Manifests with Git SHA Tag)
┌────────────────────────────────────────────────────────┐
│                   GitHub Repository                    │
│             (Single Source of Truth: /k8s)             │
└────────────────────────────────────────────────────────┘
           │
           ▼ (Automated Pull & Reconciliation)
┌────────────────────────────────────────────────────────┐
│                 ArgoCD GitOps Engine                   │
│  ├─ Automated Drift Detection & Self-Healing           │
│  └─ Zero-Downtime Rolling Update Reconciliation       │
└────────────────────────────────────────────────────────┘
           │
           ▼
┌────────────────────────────────────────────────────────┐
│             Kubernetes Cluster (Namespace: devsecops-prod) │
│                                                        │
│             [ NGINX Ingress Controller ]               │
│                   │                │                   │
│          Path: /  │                │ Path: /api        │
│                   ▼                ▼                   │
│          [ Frontend Pods ]   [ Backend Pods ]          │
│             (React JS)          (FastAPI)              │
│                                  │        │            │
│                       Cache Sync │        │ Persist    │
│                                  ▼        ▼            │
│                            [ Redis ]  [ PostgreSQL ]   │
🛠 Tech Stack & Tools
Application Tier:

Frontend: React.js, TailwindCSS, Nginx (Reverse Proxy for static assets)

Backend: FastAPI (Python 3.11), SQLAlchemy, Uvicorn

Database: PostgreSQL 15 (Persistent Storage)

Cache: Redis 7 (In-Memory Datastore)

Infrastructure & Orchestration:

Cloud: AWS EC2 (Ubuntu 24.04 LTS)

Kubernetes: Multi-Node Kind Cluster (1 Control-Plane, 2 Worker Nodes)

Ingress: NGINX Ingress Controller (Path-based prefix routing)

DevSecOps & CI/CD:

Automation: GitHub Actions

SAST & Linting: Bandit, Flake8

Vulnerability Scanning: Aqua Security Trivy (Filesystem, Config, & Container Images)

Registry: Docker Hub (abhiraj328)

GitOps & Delivery:

GitOps Controller: ArgoCD (Continuous delivery, automated self-healing, declarative drift correction)

📁 Repository Structure

devsecops-microservices/
├── .github/
│   └── workflows/
│       └── devsecops.yml        # End-to-end DevSecOps CI/CD pipeline
├── backend/
│   ├── app/                    # FastAPI application source code
│   ├── Dockerfile              # Multi-stage container definition
│   └── requirements.txt
├── frontend/
│   ├── src/                    # React UI source code
│   ├── Dockerfile              # Production Nginx multi-stage build
│   └── package.json
├── k8s/
│   ├── namespace.yaml          # Isolated namespace: devsecops-prod
│   ├── config-secret.yaml      # Environment secrets & database credentials
│   ├── postgres.yaml           # PostgreSQL Stateful Deployment & Service
│   ├── redis.yaml              # Redis In-Memory Cache Deployment & Service
│   ├── backend.yaml            # FastAPI Deployment & ClusterIP Service
│   ├── frontend.yaml           # React Deployment & ClusterIP Service
│   ├── ingress.yaml            # NGINX Ingress routing rules
│   └── argocd-app.yaml         # Declarative ArgoCD Application definition
└── README.md

🔒 Shift-Left Security Pipeline
The CI pipeline runs automatically on every pull request and push to the main branch:

Static Analysis & SAST:

Python AST parsing and vulnerability scans using Bandit (bandit -r backend/ -ll).

PEP8 standard compliance and static linting using Flake8.

Dependency Audit:

Node dependency security scan using npm audit --audit-level=high.

Container & Filesystem CVE Audit:

High and Critical severity vulnerability scanning on local filesystem and container images using Trivy.

Registry Authentication & Multi-arch Push:

Hardened container images are tagged with the specific commit SHA (${{ github.sha }}) and latest, then pushed securely to Docker Hub.

GitOps Manifest Update:

Pipeline automatically commits the newly built image SHA tag into k8s/backend.yaml and k8s/frontend.yaml using a bot account with [skip ci].

🚀 GitOps & Automated Rolling Deployment
The deployment lifecycle is managed entirely via ArgoCD:

Declarative Source of Truth: Cluster state tracks the k8s/ directory in this GitHub repository.

Automated Self-Healing (selfHeal: true): Any unauthorized manual mutations or configuration drifts directly applied to the cluster are automatically rolled back to match Git.

Automated Pruning (prune: true): Deprecated resources deleted from the repository are cleaned up inside the cluster automatically.

Zero-Downtime Rollouts: Updates to image tags trigger rolling updates across replica sets without application downtime.

⚡ Deployment & Verification
1. Ingress Path Routing
Traffic enters through the NGINX Ingress Controller on port 80:

/ routes to frontend-service:80

/api routes to backend-service:8000 (/api/v1/data endpoint for PostgreSQL persistence)

2. Live Verification Commands

# Check running application pods
kubectl get pods -n devsecops-prod

# Verify Ingress routing rules
kubectl get ingress -n devsecops-prod

# Check ArgoCD sync status
kubectl get application devsecops-microservices -n argocd

# Verify image commit SHA on live deployment
kubectl get deployment backend-deployment -n devsecops-prod \
  -o jsonpath='{.spec.template.spec.containers[0].image}'; echo

---

## 📊 Observability & Monitoring (Prometheus & Grafana)

The cluster is continuously monitored via the **kube-prometheus-stack**:

* **Prometheus:** Scrapes node-level metrics (via Node Exporters), Kubernetes API objects (via Kube-State-Metrics), and application pods.
* **Grafana:** Visualizes cluster resources, memory/CPU saturation, and pod network I/O in the `devsecops-prod` namespace.

```bash
# Forward Grafana to port 3000
kubectl port-forward svc/monitoring-stack-grafana -n monitoring --address 0.0.0.0 31586:80


👤 Author
Abhishek Kumar

GitHub: @abhishek85607

Docker Hub: @abhiraj328
