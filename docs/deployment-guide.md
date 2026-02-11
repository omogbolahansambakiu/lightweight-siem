# Deployment Guide

## Prerequisites

- Docker & Docker Compose (for container deployment)
- 8GB RAM minimum (16GB recommended)
- 50GB disk space
- Ubuntu 20.04+ or similar Linux distribution

## Quick Start (Docker Compose)

1. **Clone repository**
```bash
git clone https://github.com/yourusername/lightweight-siem.git
cd lightweight-siem
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings
nano .env
```

3. **Start services**
```bash
make up
# Or: docker-compose up -d
```

4. **Initialize indices**
```bash
make setup-indices
```

5. **Access dashboard**
```
http://localhost:3000
```

## Production Deployment

### Kubernetes

1. **Create namespace**
```bash
kubectl create namespace siem
```

2. **Apply configurations**
```bash
kubectl apply -f deployment/kubernetes/
```

3. **Verify pods**
```bash
kubectl get pods -n siem
```

### AWS (Terraform)

1. **Initialize Terraform**
```bash
cd deployment/terraform
terraform init
```

2. **Plan deployment**
```bash
terraform plan
```

3. **Apply**
```bash
terraform apply
```

## Configuration

### OpenSearch

Edit `config/opensearch/opensearch.yml`:
```yaml
cluster.name: siem-production
network.host: 0.0.0.0
```

### Detection Rules

Place YAML rules in `rules/` directory:
```yaml
name: "My Custom Rule"
severity: "HIGH"
detection:
  selection:
    event.category: "authentication"
  condition: "count > 5"
```

### Notifications

Configure in `.env`:
```bash
SMTP_ENABLED=true
SMTP_SERVER=smtp.gmail.com
SMTP_USER=your-email@gmail.com
```

## Troubleshooting

### Services won't start
```bash
docker-compose logs <service-name>
```

### No logs appearing
```bash
# Check Redis queue
redis-cli LLEN events:raw
```

### Alerts not firing
```bash
# Check detection engine logs
docker-compose logs detection-engine
```
