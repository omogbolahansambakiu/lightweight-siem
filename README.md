# Lightweight SIEM (Security Information and Event Management)

A modern, scalable, open-source SIEM solution designed for real-time security monitoring and threat detection.

## Overview

This SIEM platform provides:
- **Real-time log ingestion** from multiple sources (Syslog, Windows Events, Web Servers, Firewalls)
- **Intelligent parsing and normalization** to ECS (Elastic Common Schema) format
- **Advanced threat detection** with customizable YAML-based rules
- **Automated alerting** via Email, Slack, PagerDuty, and Webhooks
- **Interactive dashboard** for security monitoring and investigation
- **Scalable architecture** using OpenSearch, Redis, and microservices

## Architecture

```
Log Sources → Collectors → Redis Queue → Parser Engine → OpenSearch
                                              ↓
                                      Detection Engine
                                              ↓
                                       Alert Manager
                                              ↓
                                   Email/Slack/PagerDuty
```

## Features

### Core Capabilities
- ✅ Multi-source log collection (Syslog, Filebeat, Winlogbeat, HTTP API)
- ✅ Automatic log parsing and field extraction
- ✅ GeoIP enrichment for IP addresses
- ✅ DNS reverse lookup enrichment
- ✅ Threat intelligence integration
- ✅ Real-time detection engine with correlation rules
- ✅ Severity-based alert routing
- ✅ Alert deduplication and throttling
- ✅ RESTful API for integration
- ✅ Modern React dashboard

### Detection Capabilities
- SSH brute force detection
- Failed login threshold monitoring
- Port scan detection
- Web attack detection (SQL injection, XSS)
- Privilege escalation monitoring
- Data exfiltration detection
- Unusual traffic pattern detection
- Custom rule creation via YAML

## Quick Start

### Prerequisites
- Docker & Docker Compose
- 8GB RAM minimum (16GB recommended)
- 50GB disk space

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/lightweight-siem.git
cd lightweight-siem
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

3. **Start services**
```bash
make up
```

4. **Access the dashboard**
```
http://localhost:3000
```

Default credentials: `admin / changeme`

### Initial Setup

1. **Load index templates**
```bash
make setup-indices
```

2. **Import detection rules**
```bash
make load-rules
```

3. **Configure data sources**
   - Edit `config/filebeat/filebeat.yml` for log file paths
   - Edit `config/siem/config.yml` for SIEM settings

## Configuration

### Environment Variables (.env)
```bash
# OpenSearch
OPENSEARCH_HOST=opensearch
OPENSEARCH_PORT=9200
OPENSEARCH_USER=admin
OPENSEARCH_PASSWORD=admin

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Alert Notifications
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
PAGERDUTY_API_KEY=your-pagerduty-key
```

### Detection Rules

Rules are defined in YAML format under `rules/`:

```yaml
# rules/authentication/ssh_bruteforce.yml
name: "SSH Brute Force Attack"
description: "Detects multiple failed SSH login attempts"
severity: "HIGH"
enabled: true

detection:
  selection:
    event.category: "authentication"
    event.outcome: "failure"
    source.port: 22
  
  condition: "count > 5"
  timeframe: "5m"
  groupby: ["source.ip"]

actions:
  - type: "alert"
    notification: ["slack", "email"]
```

## Components

### Detection Engine
- Processes events from Redis queue
- Applies detection rules
- Performs event correlation
- Enriches with GeoIP and threat intel
- Located in: `detection-engine/`

### Alert Manager
- Receives alerts from Detection Engine
- Handles deduplication and throttling
- Routes to notification channels
- Located in: `alert-manager/`

### API Server
- RESTful API for dashboard and integrations
- FastAPI-based Python service
- Authentication and rate limiting
- Located in: `api/`

### Frontend Dashboard
- React-based web interface
- Real-time alert monitoring
- Investigation tools
- Visualization charts
- Located in: `frontend/`

## API Documentation

### Endpoints

#### Alerts
- `GET /api/v1/alerts` - List alerts
- `GET /api/v1/alerts/{id}` - Get alert details
- `PUT /api/v1/alerts/{id}/status` - Update alert status

#### Search
- `POST /api/v1/search` - Search events
- `POST /api/v1/search/aggregate` - Aggregate queries

#### Health
- `GET /api/health` - Service health check
- `GET /api/metrics` - Prometheus metrics

See [API Reference](docs/api-reference.md) for detailed documentation.

## Development

### Running Tests
```bash
make test
```

### Test Coverage
```bash
make coverage
```

### Linting
```bash
make lint
```

### Development Mode
```bash
make dev
```

## Deployment

### Docker Compose (Development)
```bash
docker-compose up -d
```

### Kubernetes (Production)
```bash
kubectl apply -f deployment/kubernetes/
```

### Terraform (AWS)
```bash
cd deployment/terraform
terraform init
terraform plan
terraform apply
```

## Monitoring

### Prometheus Metrics
- Detection engine processing rate
- Alert generation rate
- Parser success/failure rates
- Queue depths
- API response times

Access Prometheus: `http://localhost:9090`

### Grafana Dashboards
- Security Overview
- Alert Management
- Investigation Dashboard

Access Grafana: `http://localhost:3001`

## Performance Tuning

### For High Volume Environments

1. **Scale Detection Engine**
```bash
docker-compose up -d --scale detection-engine=4
```

2. **Increase Redis Memory**
```yaml
# docker-compose.yml
redis:
  command: redis-server --maxmemory 4gb
```

3. **OpenSearch Cluster**
   - Add more data nodes
   - Increase heap size
   - Configure index sharding

## Security Considerations

### Authentication
- Change default credentials immediately
- Enable SSL/TLS for all services
- Use strong passwords
- Implement API key rotation

### Network Security
- Use firewall rules
- Enable encryption in transit
- Isolate SIEM network segment
- Configure VPN for remote access

### Data Protection
- Enable OpenSearch encryption at rest
- Regular backups
- Secure secret management
- Audit logging

## Troubleshooting

### Common Issues

**Logs not appearing**
```bash
# Check collector status
docker-compose logs filebeat

# Verify Redis queue
redis-cli LLEN events:raw
```

**Alerts not firing**
```bash
# Check detection engine logs
docker-compose logs detection-engine

# Test rule manually
python scripts/testing/test_detection_rules.py
```

**Dashboard not loading**
```bash
# Check API connectivity
curl http://localhost:8000/api/health

# Check frontend logs
docker-compose logs frontend
```

See [Troubleshooting Guide](docs/troubleshooting.md) for more help.

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md).

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Roadmap

- [ ] Machine learning-based anomaly detection
- [ ] MITRE ATT&CK framework mapping
- [ ] Automated threat hunting
- [ ] Integration with SOAR platforms
- [ ] Mobile app for alert management
- [ ] Advanced user behavior analytics (UBA)
- [ ] Threat intelligence feed aggregation

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/lightweight-siem/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/lightweight-siem/discussions)

## Acknowledgments

- Built with OpenSearch, Redis, FastAPI, and React
- Inspired by ELK Stack, Wazuh, and Security Onion
- Thanks to the open-source security community

---

**⚠️ Important**: This SIEM is designed for security monitoring. Ensure compliance with your organization's security policies and relevant regulations (GDPR, HIPAA, etc.) when deploying.
