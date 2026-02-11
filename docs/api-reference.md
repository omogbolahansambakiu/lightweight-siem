# API Reference

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Include API key in header:
```
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### Health Check

**GET** `/api/health`

Returns system health status.

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "redis": "up",
    "opensearch": "up"
  }
}
```

### List Alerts

**GET** `/api/v1/alerts`

**Query Parameters:**
- `severity` (optional): Filter by severity (CRITICAL, HIGH, MEDIUM, LOW)
- `limit` (optional): Max results (default: 100, max: 1000)
- `offset` (optional): Pagination offset

**Response:**
```json
{
  "alerts": [
    {
      "id": "alert-123",
      "rule": {
        "name": "SSH Brute Force",
        "severity": "HIGH"
      },
      "timestamp": "2024-01-15T10:30:00Z",
      "status": "new"
    }
  ],
  "total": 42
}
```

### Get Alert Details

**GET** `/api/v1/alerts/{alert_id}`

**Response:**
```json
{
  "id": "alert-123",
  "rule": {
    "id": "auth-001",
    "name": "SSH Brute Force",
    "severity": "HIGH"
  },
  "event": {
    "source": {
      "ip": "192.168.1.100"
    }
  }
}
```

### Search Events

**POST** `/api/v1/search`

**Request Body:**
```json
{
  "query": "source.ip:192.168.1.100",
  "start_time": "2024-01-15T00:00:00Z",
  "end_time": "2024-01-15T23:59:59Z"
}
```

**Response:**
```json
{
  "hits": [
    {
      "@timestamp": "2024-01-15T10:30:00Z",
      "source": {
        "ip": "192.168.1.100"
      },
      "message": "Authentication failure"
    }
  ],
  "total": 156
}
```

### Dashboard Stats

**GET** `/api/v1/dashboard/stats`

**Response:**
```json
{
  "alerts_today": 42,
  "events_today": 15234,
  "top_sources": [
    {"ip": "192.168.1.100", "count": 523}
  ]
}
```
