from fastapi import APIRouter
from datetime import datetime, timedelta
from collections import defaultdict
from opensearchpy import OpenSearch
import re

router = APIRouter()

# Connect to OpenSearch - uses docker-compose service name
client = OpenSearch(
    hosts=[{"host": "opensearch", "port": 9200}],
    http_auth=("admin", "admin"),
    use_ssl=False
)


@router.get("/dashboard")
async def get_dashboard_stats(range: str = "24h"):
    """
    Returns dashboard data matching the App.jsx expected structure:
    {
        stats: {
            total_alerts, critical_alerts, events_per_sec, failed_logins,
            timeline: [{ time, critical, high, medium }],
            by_severity: [{ severity, count }],
            top_ips: [{ ip, count }],
            auth_events: [{ hour, failed, success }]
        },
        alerts: [{
            alert_id, timestamp, rule_name, severity,
            evidence: { source_ip, user }
        }]
    }
    """
    hours_map = {"1h": 1, "24h": 24, "7d": 168, "30d": 720}
    hours = hours_map.get(range, 24)
    since = (datetime.utcnow() - timedelta(hours=hours)).isoformat()

    try:
        response = client.search(
            index="siem-*",
            body={
                "size": 100,
                "sort": [{"@timestamp": "desc"}],
                "query": {
                    "range": {
                        "@timestamp": {"gte": since}
                    }
                }
            }
        )

        hits = response["hits"]["hits"]
        total_events = response["hits"]["total"]["value"]

        # ── Build alerts list ──────────────────────────────────────────────
        alerts = []
        for hit in hits:
            source = hit["_source"]
            message = source.get("message", "")

            # Skip internal error messages from containers
            if "alert-manager" in message or "detection-engine" in message:
                continue

            alerts.append({
                "alert_id": hit["_id"],
                "timestamp": source.get("@timestamp"),
                "rule_name": classify_rule(message),
                "severity": classify_severity(message),
                "evidence": {
                    "source_ip": extract_ip(message),
                    "user": extract_user(message)
                }
            })

       
        severity_counts = defaultdict(int)
        for alert in alerts:
            severity_counts[alert["severity"]] += 1

        by_severity = [
            {"severity": severity, "count": count}
            for severity, count in severity_counts.items()
        ]

       
        ip_counts = defaultdict(int)
        for alert in alerts:
            ip = alert["evidence"]["source_ip"]
            if ip != "N/A":
                ip_counts[ip] += 1

        top_ips = [
            {"ip": ip, "count": count}
            for ip, count in sorted(
                ip_counts.items(), key=lambda x: x[1], reverse=True
            )[:5]
        ]

        
        auth_by_hour = defaultdict(lambda: {"failed": 0, "success": 0})
        for hit in hits:
            message = hit["_source"].get("message", "")
            timestamp = hit["_source"].get("@timestamp", "")
            hour = timestamp[:13] + ":00" if timestamp else "unknown"

            if "Failed password" in message or "Invalid user" in message:
                auth_by_hour[hour]["failed"] += 1
            elif "Accepted password" in message or "session opened" in message:
                auth_by_hour[hour]["success"] += 1

        auth_events = [
            {"hour": hour, "failed": v["failed"], "success": v["success"]}
            for hour, v in sorted(auth_by_hour.items())
        ]

        
        timeline_data = defaultdict(lambda: {"critical": 0, "high": 0, "medium": 0})
        for alert in alerts:
            timestamp = alert["timestamp"] or ""
            if timestamp:
                # Round to nearest 4h bucket
                hour = int(timestamp[11:13])
                bucket = (hour // 4) * 4
                time_key = f"{bucket:02d}:00"
                sev = alert["severity"]
                if sev in ("critical", "high", "medium"):
                    timeline_data[time_key][sev] += 1

        timeline = [
            {"time": time, "critical": v["critical"], "high": v["high"], "medium": v["medium"]}
            for time, v in sorted(timeline_data.items())
        ]

        failed_logins = sum(
            1 for hit in hits
            if "Failed password" in hit["_source"].get("message", "")
            or "Invalid user" in hit["_source"].get("message", "")
        )

        events_per_sec = round(total_events / (hours * 3600), 4)

        return {
            "stats": {
                "total_alerts": len(alerts),
                "critical_alerts": severity_counts.get("critical", 0),
                "events_per_sec": events_per_sec,
                "failed_logins": failed_logins,
                "timeline": timeline,
                "by_severity": by_severity,
                "top_ips": top_ips,
                "auth_events": auth_events
            },
            "alerts": alerts[:10]  
        }

    except Exception as e:
        print(f"OpenSearch error: {e}")
        
        return {
            "stats": {
                "total_alerts": 0,
                "critical_alerts": 0,
                "events_per_sec": 0,
                "failed_logins": 0,
                "timeline": [],
                "by_severity": [],
                "top_ips": [],
                "auth_events": []
            },
            "alerts": []
        }


# ── Helper functions ───────────────────────────────────────────────────────────

def classify_severity(message: str) -> str:
    """Maps log message content to severity levels used by App.jsx badges."""
    msg = message.lower()
    if any(x in msg for x in ["malware", "trojan", "ransomware", "rootkit"]):
        return "critical"
    elif any(x in msg for x in ["failed password", "invalid user", "block", "attack"]):
        return "high"
    elif any(x in msg for x in ["scan", "probe", "sudo", "suspicious"]):
        return "medium"
    return "low"


def classify_rule(message: str) -> str:
    """Maps log message to a human-readable rule name for AlertsTable."""
    if "Failed password" in message:
        return "Failed Login Attempt"
    elif "Invalid user" in message:
        return "Invalid User Login Attempt"
    elif "Accepted password" in message:
        return "Successful Login"
    elif "BLOCK" in message or "UFW" in message:
        return "Firewall Block"
    elif "Malware" in message or "Trojan" in message:
        return "Malware Detected"
    elif "scan" in message.lower():
        return "Port Scan Detected"
    elif "sudo" in message:
        return "Sudo Command Executed"
    elif "session opened" in message:
        return "Session Opened"
    elif "session closed" in message:
        return "Session Closed"
    return "Security Event"


def extract_ip(message: str) -> str:
    """Extracts first IPv4 address from log message for evidence.source_ip."""
    match = re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', message)
    return match.group(0) if match else "N/A"


def extract_user(message: str) -> str:
    """Extracts username from log message for evidence.user."""
    # SSH format: "for USERNAME from"
    match = re.search(r'for (\w+) from', message)
    if match:
        return match.group(1)
    # Sudo format: "USER : TTY"
    match = re.search(r'^[\w-]+\s+(\w+)\s+:', message)
    if match:
        return match.group(1)
    return "N/A"