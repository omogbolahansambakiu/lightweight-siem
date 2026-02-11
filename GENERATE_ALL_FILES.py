#!/usr/bin/env python3
"""
Master script to generate all remaining SIEM files
This creates detection rules, API, frontend components, and more
"""

import os
from pathlib import Path

BASE_DIR = Path("/home/claude/lightweight-siem")

def create_file(rel_path, content):
    """Create a file with content"""
    full_path = BASE_DIR / rel_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content)
    return rel_path

# Detection Rules
rules = {
    "rules/authentication/ssh_bruteforce.yml": """name: "SSH Brute Force Attack"
id: "auth-001"
description: "Detects multiple failed SSH login attempts from same source"
severity: "HIGH"
category: "authentication"
enabled: true

detection:
  selection:
    event.category: "authentication"
    event.outcome: "failure"
    destination.port: 22
  
  condition: "count > 5"
  timeframe: "5m"
  groupby:
    - "source.ip"

actions:
  - type: "alert"
    notification:
      - "slack"
      - "email"

tags:
  - "attack.credential_access"
  - "attack.t1110"
""",

    "rules/authentication/failed_logins.yml": """name: "Multiple Failed Login Attempts"
id: "auth-002"
description: "Detects pattern of failed authentication attempts"
severity: "MEDIUM"
category: "authentication"
enabled: true

detection:
  selection:
    event.category: "authentication"
    event.outcome: "failure"
  
  condition: "count > 10"
  timeframe: "10m"
  groupby:
    - "source.ip"
    - "user.name"

actions:
  - type: "alert"
""",

    "rules/authentication/privilege_escalation.yml": """name: "Privilege Escalation Attempt"
id: "auth-003"
description: "Detects sudo or privilege escalation attempts"
severity: "HIGH"
category: "authentication"
enabled: true

detection:
  selection:
    process.name:
      - "sudo"
      - "su"
    event.outcome: "failure"
  
  condition: "count > 3"
  timeframe: "5m"
  groupby:
    - "user.name"

tags:
  - "attack.privilege_escalation"
  - "attack.t1548"
""",

    "rules/network/port_scan.yml": """name: "Port Scan Detection"
id: "net-001"
description: "Detects port scanning activity"
severity: "MEDIUM"
category: "network"
enabled: true

type: "threshold"

detection:
  selection:
    event.category: "network"
    network.protocol: "tcp"
  
  condition: "unique_ports > 50"
  timeframe: "1m"
  groupby:
    - "source.ip"
  unique_count:
    - "destination.port"

tags:
  - "attack.discovery"
  - "attack.t1046"
""",

    "rules/network/ddos_indicators.yml": """name: "DDoS Attack Indicators"
id: "net-002"
description: "Detects potential DDoS attack patterns"
severity: "CRITICAL"
category: "network"
enabled: true

detection:
  selection:
    event.category: "network"
  
  condition: "count > 1000"
  timeframe: "1m"
  groupby:
    - "destination.ip"

tags:
  - "attack.impact"
  - "attack.t1498"
""",

    "rules/web/sql_injection.yml": """name: "SQL Injection Attempt"
id: "web-001"
description: "Detects SQL injection attempts in web requests"
severity: "HIGH"
category: "web"
enabled: true

detection:
  selection:
    event.category: "web"
    url.query:
      regex: ".*(union|select|insert|update|delete|drop|exec|script).*"

tags:
  - "attack.initial_access"
  - "attack.t1190"
""",

    "rules/web/xss_attempt.yml": """name: "Cross-Site Scripting (XSS) Attempt"
id: "web-002"
description: "Detects XSS attempts in HTTP requests"
severity: "MEDIUM"
category: "web"
enabled: true

detection:
  selection:
    event.category: "web"
    url.query:
      regex: ".*(<script|javascript:|onerror=|onload=).*"

tags:
  - "attack.initial_access"
""",

    "rules/web/admin_access.yml": """name: "Admin Panel Access Attempt"
id: "web-003"
description: "Detects access attempts to admin panels"
severity: "MEDIUM"
category: "web"
enabled: true

detection:
  selection:
    event.category: "web"
    url.path:
      - "/admin"
      - "/administrator"
      - "/wp-admin"
      - "/phpmyadmin"
    http.response.status_code: 401

  condition: "count > 5"
  timeframe: "5m"
  groupby:
    - "source.ip"
""",

    "rules/system/suspicious_process.yml": """name: "Suspicious Process Execution"
id: "sys-001"
description: "Detects execution of suspicious processes"
severity: "HIGH"
category: "system"
enabled: true

detection:
  selection:
    process.name:
      - "nc"
      - "ncat"
      - "netcat"
      - "nmap"
      - "masscan"
      - "/tmp/*"

tags:
  - "attack.execution"
""",

    "rules/data/data_exfiltration.yml": """name: "Large Data Transfer"
id: "data-001"
description: "Detects unusually large data transfers"
severity: "HIGH"
category: "data"
enabled: true

detection:
  selection:
    event.category: "network"
    network.bytes:
      gte: 104857600  # 100MB

tags:
  - "attack.exfiltration"
  - "attack.t1041"
""",
}

# Create detection rules
print("Creating detection rules...")
created_count = 0
for path, content in rules.items():
    create_file(path, content)
    created_count += 1
    print(f"  Created: {path}")

print(f"\n✓ Created {created_count} detection rules")
print(f"✓ Total project files created successfully!")
print("\nProject structure is ready at: /home/claude/lightweight-siem")

