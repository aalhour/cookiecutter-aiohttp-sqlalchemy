# Kubernetes Deployment

This directory contains Kubernetes manifests for deploying example_web_app.

## Prerequisites

- Kubernetes cluster (1.25+)
- kubectl configured
- Container image built and pushed to a registry

## Quick Start

```bash
# Create namespace and deploy all resources
kubectl apply -k k8s/

# Or apply individually
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/serviceaccount.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

## Manifests

| File | Description |
|------|-------------|
| `namespace.yaml` | Namespace for isolation |
| `configmap.yaml` | Non-sensitive configuration |
| `secret.yaml` | Sensitive configuration (passwords, API keys) |
| `serviceaccount.yaml` | Service account for pod identity |
| `deployment.yaml` | Main API deployment |
| `service.yaml` | ClusterIP service |
| `ingress.yaml` | Ingress for external access |
| `hpa.yaml` | Horizontal Pod Autoscaler |
| `pdb.yaml` | Pod Disruption Budget |
| `worker-deployment.yaml` | Background worker deployment |
| `kustomization.yaml` | Kustomize configuration |

## Configuration

### Update Secrets

**Important:** Change the default secrets before deploying to production!

```bash
# Edit secrets
kubectl edit secret example_web_app-secrets -n example_web_app

# Or create from literal
kubectl create secret generic example_web_app-secrets \
  --namespace=example_web_app \
  --from-literal=DB_PASSWORD=your-secure-password \
  --from-literal=REDIS_PASSWORD= \
  --from-literal=SENTRY_DSN=
```

### Update Ingress

Edit `ingress.yaml` to configure:
- Your domain name
- TLS certificate (with cert-manager)
- Any additional annotations

## Using Kustomize

```bash
# Preview what will be applied
kubectl kustomize k8s/

# Apply with kustomize
kubectl apply -k k8s/

# For different environments, create overlays:
# k8s/
# ├── base/           # Base manifests
# │   └── kustomization.yaml
# └── overlays/
#     ├── dev/        # Dev environment
#     ├── staging/    # Staging environment
#     └── prod/       # Production environment
```

## Deploy Worker

The background worker is optional. To deploy it:

```bash
kubectl apply -f k8s/worker-deployment.yaml
```

Or uncomment the worker in `kustomization.yaml` and apply with kustomize.

## Monitoring

The deployment includes Prometheus annotations for scraping metrics:

```yaml
annotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "9999"
  prometheus.io/path: "/metrics"
```

## Health Checks

The deployment uses three types of probes:

- **Liveness Probe** (`/api/-/live`): Basic process health
- **Readiness Probe** (`/api/-/ready`): Full dependency health
- **Startup Probe** (`/api/-/health`): Initial startup check

## Scaling

### Manual Scaling

```bash
kubectl scale deployment example_web_app --replicas=5 -n example_web_app
```

### Automatic Scaling

The HPA is configured to scale based on:
- CPU utilization (target: 70%)
- Memory utilization (target: 80%)

Adjust `hpa.yaml` for your needs.

## Troubleshooting

```bash
# Check pod status
kubectl get pods -n example_web_app

# View logs
kubectl logs -f deployment/example_web_app -n example_web_app

# Describe deployment
kubectl describe deployment example_web_app -n example_web_app

# Check events
kubectl get events -n example_web_app --sort-by='.lastTimestamp'

# Port forward for local testing
kubectl port-forward svc/example_web_app 8080:80 -n example_web_app
```

