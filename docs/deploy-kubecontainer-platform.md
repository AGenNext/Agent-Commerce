# Deploy on kubecontainer Platform

This deploys the Foundation Agent-Commerce Protocol Service into the shared `kubecontainer` Kubernetes namespace.

Public test port: `30080`.

## Prerequisites

- Kubernetes or k3s is running on the VPS.
- `kubectl` is configured on the VPS.
- The shared `kubecontainer` namespace exists.
- The GHCR image is available: `ghcr.io/agennext/agent-commerce-protocol:latest`.

Create the namespace only when provisioning a new platform cluster:

```bash
kubectl apply -f k8s/kubecontainer/namespace.yaml
```

The namespace is intentionally excluded from the application kustomization so removing this service cannot delete other platform workloads.

## Validate Manifests

Render the resources before deployment:

```bash
kubectl kustomize k8s/kubecontainer
```

When the cluster supports server-side dry runs:

```bash
kubectl apply --dry-run=server -k k8s/kubecontainer
```

## Deploy

From the repository root on the VPS:

```bash
git pull origin main
kubectl apply -k k8s/kubecontainer
kubectl -n kubecontainer rollout status deployment/agent-commerce-protocol --timeout=120s
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
curl -fsS http://127.0.0.1:30080/health
curl -fsS http://127.0.0.1:30080/schema
curl -fsS http://127.0.0.1:30080/examples
```

From outside the VPS, replace `<VPS_PUBLIC_IP>`:

```bash
curl -fsS http://<VPS_PUBLIC_IP>:30080/health
```

## Validate a Protocol Payload

```bash
curl --fail-with-body -X POST http://127.0.0.1:30080/validate \
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
kubectl -n kubecontainer rollout status deployment/agent-commerce-protocol --timeout=120s && \
curl -fsS http://127.0.0.1:30080/health
```

## Remove Only This Service

This command removes only resources declared by the application kustomization. It does not delete the shared namespace:

```bash
kubectl delete -k k8s/kubecontainer
```

Confirm that the namespace and unrelated workloads remain:

```bash
kubectl get namespace kubecontainer
kubectl -n kubecontainer get all
```

## Production Notes

NodePort is intended for immediate VPS testing. For production, use the kubecontainer ingress layer, terminate TLS there, restrict direct NodePort access at the firewall, and deploy an immutable image tag or digest rather than `latest`.
