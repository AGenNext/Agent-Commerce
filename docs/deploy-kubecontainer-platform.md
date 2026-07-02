# Deploy on kubecontainer Platform

This deploys the Foundation Agent-Commerce Protocol Service into the kubecontainer Kubernetes platform.

Target namespace:

```text
kubecontainer
```

Public test port:

```text
30080
```

## Prerequisites

- Kubernetes or k3s is running on the VPS
- `kubectl` is configured on the VPS
- The GHCR image is available:

```text
ghcr.io/agennext/agent-commerce-protocol:latest
```

## Deploy

From the repo root on the VPS:

```bash
git pull origin main
kubectl apply -k k8s/kubecontainer
kubectl -n kubecontainer rollout status deployment/agent-commerce-protocol
```

## Verify Inside Cluster

```bash
kubectl -n kubecontainer get pods
kubectl -n kubecontainer get svc
kubectl -n kubecontainer logs deploy/agent-commerce-protocol --tail=100
```

## Verify Through NodePort

From the VPS:

```bash
curl http://127.0.0.1:30080/health
curl http://127.0.0.1:30080/schema
curl http://127.0.0.1:30080/examples
```

From outside the VPS, replace `<VPS_PUBLIC_IP>`:

```bash
curl http://<VPS_PUBLIC_IP>:30080/health
```

## Validate a Protocol Payload

```bash
curl -X POST http://127.0.0.1:30080/validate \
  -H 'Content-Type: application/json' \
  -d '{
    "payload": {
      "ucp_version": "0.1-profile",
      "type": "commerce.action.request",
      "action": "product.create",
      "actor": {"type": "agent", "id": "agent_store_helper"},
      "resource": {"type": "product"},
      "input": {"name": "Notebook", "price": 99, "currency": "INR", "stock": 50},
      "trace_id": "trace_001"
    }
  }'
```

## One-command VPS Deploy

```bash
kubectl apply -k k8s/kubecontainer && \
kubectl -n kubecontainer rollout status deployment/agent-commerce-protocol && \
curl -fsS http://127.0.0.1:30080/health
```

## Remove

```bash
kubectl delete -k k8s/kubecontainer
```

## Production Notes

NodePort is for immediate VPS testing. For production public domains, front this service with the kubecontainer platform ingress layer, usually Caddy or Kubernetes Ingress, and terminate TLS there.
