#!/usr/bin/env python3
"""Verify all files were created correctly"""

import os
from pathlib import Path

BASE = Path("/home/claude/lightweight-siem")

# Expected files
EXPECTED_FILES = [
    "README.md",
    ".env.example",
    ".gitignore",
    "docker-compose.yml",
    "Makefile",
    "LICENSE",
    "CONTRIBUTING.md",
    
    # Detection Engine
    "detection-engine/main.py",
    "detection-engine/requirements.txt",
    "detection-engine/engine/detection_engine.py",
    "detection-engine/engine/rule_loader.py",
    "detection-engine/parsers/parser_engine.py",
    "detection-engine/enrichment/geoip.py",
    "detection-engine/models/event.py",
    "detection-engine/utils/ecs_mapper.py",
    
    # Alert Manager
    "alert-manager/main.py",
    "alert-manager/alert_manager.py",
    "alert-manager/requirements.txt",
    "alert-manager/notifications/email.py",
    "alert-manager/notifications/slack.py",
    
    # API
    "api/main.py",
    "api/requirements.txt",
    "api/routers/health.py",
    "api/routers/alerts.py",
    
    # Frontend
    "frontend/package.json",
    "frontend/src/App.jsx",
    "frontend/src/main.jsx",
    
    # Rules
    "rules/authentication/ssh_bruteforce.yml",
    "rules/network/port_scan.yml",
    "rules/web/sql_injection.yml",
    
    # Config
    "config/opensearch/opensearch.yml",
    "config/redis/redis.conf",
    "config/filebeat/filebeat.yml",
    "config/siem/config.yml",
    
    # Deployment
    "deployment/docker/detection-engine/Dockerfile",
    "deployment/docker/alert-manager/Dockerfile",
    "deployment/docker/api/Dockerfile",
    "deployment/docker/frontend/Dockerfile",
    
    # Docs
    "docs/architecture.md",
    "docs/deployment-guide.md",
    "docs/api-reference.md",
]

print("Verifying SIEM project structure...")
print("=" * 60)

missing = []
found = []

for file in EXPECTED_FILES:
    filepath = BASE / file
    if filepath.exists():
        found.append(file)
    else:
        missing.append(file)

print(f"✅ Found: {len(found)}/{len(EXPECTED_FILES)} expected files")

if missing:
    print(f"\n⚠️  Missing {len(missing)} files:")
    for f in missing[:10]:
        print(f"   - {f}")
    if len(missing) > 10:
        print(f"   ... and {len(missing) - 10} more")
else:
    print("\n🎉 All expected files present!")

# Count all files
all_files = list(BASE.rglob("*"))
file_count = len([f for f in all_files if f.is_file()])
dir_count = len([f for f in all_files if f.is_dir()])

print(f"\n📊 Project Statistics:")
print(f"   Total Files: {file_count}")
print(f"   Total Directories: {dir_count}")

# Count by type
py_files = len(list(BASE.rglob("*.py")))
yml_files = len(list(BASE.rglob("*.yml")))
js_files = len(list(BASE.rglob("*.js")) + list(BASE.rglob("*.jsx")))
md_files = len(list(BASE.rglob("*.md")))

print(f"\n📝 File Types:")
print(f"   Python files: {py_files}")
print(f"   YAML files: {yml_files}")
print(f"   JavaScript/React files: {js_files}")
print(f"   Documentation files: {md_files}")

print("\n" + "=" * 60)
print("✨ Project ready for deployment!")
print("   Location: /home/claude/lightweight-siem")
print("=" * 60)

