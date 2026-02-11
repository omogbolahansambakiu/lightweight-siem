# SIEM Architecture

## System Overview

The Lightweight SIEM is built on a microservices architecture with the following components:

### Core Components

1. **Log Collectors**
   - Filebeat: Collects logs from files
   - Winlogbeat: Windows Event Logs
   - Syslog Receiver: Network syslog
   - HTTP Collector: API endpoint

2. **Redis Queue**
   - Message broker for event streaming
   - Buffers events between components
   - Queues: `events:raw`, `events:parsed`, `alerts:queue`

3. **Detection Engine**
   - Parses raw logs to ECS format
   - Enriches with GeoIP, DNS, Threat Intel
   - Applies YAML-based detection rules
   - Generates alerts on rule matches

4. **Alert Manager**
   - Processes alerts from queue
   - Deduplication and throttling
   - Routes to notification channels
   - Email, Slack, PagerDuty, Webhook

5. **OpenSearch**
   - Stores all events and alerts
   - Provides search capabilities
   - Time-series data management

6. **API Server**
   - FastAPI REST API
   - Dashboard data endpoints
   - Search and investigation
   - Authentication & rate limiting

7. **Frontend**
   - React-based web interface
   - Real-time dashboards
   - Alert management
   - Investigation tools

## Data Flow

```
Log Sources → Collectors → Redis (events:raw)
                              ↓
                       Detection Engine
                       (parse, enrich, detect)
                              ↓
                       ┌──────┴──────┐
                       ↓             ↓
                  OpenSearch    Redis (alerts:queue)
                                     ↓
                              Alert Manager
                                     ↓
                         Email/Slack/PagerDuty
```

## Scaling Considerations

- **Horizontal Scaling**: Run multiple detection-engine workers
- **Queue Depth Monitoring**: Monitor Redis queue sizes
- **OpenSearch Cluster**: Add data nodes for capacity
- **Index Management**: Time-based indices with ILM policies

## Security

- TLS/SSL for all communications
- Authentication on all services
- Network isolation
- Secrets management
- Audit logging
