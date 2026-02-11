"""
Detection Engine Core

Processes events, applies rules, and generates alerts.
"""

import json
import time
import os
import threading
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import structlog
import redis
from opensearchpy import OpenSearch, helpers

from engine.rule_loader import RuleLoader
from engine.correlation import CorrelationEngine
from engine.threshold import ThresholdTracker
from parsers.parser_engine import ParserEngine
from utils.ecs_mapper import ECSMapper

logger = structlog.get_logger()


class DetectionEngine:
    """Core detection engine for processing events and generating alerts"""
    
    def __init__(self, parser_engine, enrichers, ecs_mapper):
        self.logger = logger.bind(component="detection-engine")
        self.running = False
        self.threads = []
        
        # Components
        self.parser_engine = parser_engine
        self.enrichers = enrichers
        self.ecs_mapper = ecs_mapper
        
        # Rule management
        self.rule_loader = RuleLoader()
        self.rules = self.rule_loader.load_all_rules()
        
        # Correlation and threshold tracking
        self.correlation_engine = CorrelationEngine()
        self.threshold_tracker = ThresholdTracker()
        
        # Connections
        self._init_redis()
        self._init_opensearch()
        
        # Metrics
        self.metrics = {
            "events_processed": 0,
            "events_enriched": 0,
            "alerts_generated": 0,
            "rules_matched": 0,
            "parse_errors": 0
        }
        
        self.logger.info(
            "Detection engine initialized",
            rules_loaded=len(self.rules)
        )
    
    def _init_redis(self):
        """Initialize Redis connection"""
        import os
        self.redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "redis"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=int(os.getenv("REDIS_DB", 0)),
            decode_responses=True
        )
        self.redis_client.ping()
        self.logger.info("Redis connection established")
    
    def _init_opensearch(self):
        """Initialize OpenSearch connection"""
        import os
        self.opensearch = OpenSearch(
            hosts=[{
                "host": os.getenv("OPENSEARCH_HOST", "opensearch"),
                "port": int(os.getenv("OPENSEARCH_PORT", 9200))
            }],
            http_auth=(
                os.getenv("OPENSEARCH_USER", "admin"),
                os.getenv("OPENSEARCH_PASSWORD", "admin")
            ),
            use_ssl=os.getenv("OPENSEARCH_USE_SSL", "false").lower() == "true",
            verify_certs=False,
            ssl_show_warn=False
        )
        self.opensearch.info()
        self.logger.info("OpenSearch connection established")
    
    def start(self):
        """Start processing threads"""
        self.running = True
        
        # Start worker threads
        num_workers = int(os.getenv("DETECTION_WORKERS", 2))
        for i in range(num_workers):
            thread = threading.Thread(
                target=self._worker,
                name=f"DetectionWorker-{i}",
                daemon=True
            )
            thread.start()
            self.threads.append(thread)
            self.logger.info(f"Started worker thread {i}")
        
        # Start rule reload thread
        reload_thread = threading.Thread(
            target=self._rule_reload_worker,
            name="RuleReloader",
            daemon=True
        )
        reload_thread.start()
        self.threads.append(reload_thread)
        
        self.logger.info("All worker threads started")
    
    def stop(self):
        """Stop all processing"""
        self.running = False
        
        # Wait for threads to finish
        for thread in self.threads:
            thread.join(timeout=5)
        
        self.logger.info("All threads stopped")
    
    def _worker(self):
        """Main worker loop"""
        import os
        batch_size = int(os.getenv("DETECTION_BATCH_SIZE", 100))
        poll_interval = int(os.getenv("DETECTION_POLL_INTERVAL", 1))
        
        while self.running:
            try:
                # Pull events from Redis queue
                events = self._pull_events(batch_size)
                
                if not events:
                    time.sleep(poll_interval)
                    continue
                
                # Process batch
                self._process_batch(events)
                
            except Exception as e:
                self.logger.error("Worker error", error=str(e))
                time.sleep(poll_interval)
    
    def _pull_events(self, batch_size: int) -> List[str]:
        """Pull events from Redis queue"""
        try:
            # Use RPOP for FIFO processing
            events = []
            for _ in range(batch_size):
                event = self.redis_client.rpop("events:raw")
                if event:
                    events.append(event)
                else:
                    break
            return events
        except Exception as e:
            self.logger.error("Failed to pull events from Redis", error=str(e))
            return []
    
    def _process_batch(self, raw_events: List[str]):
        """Process a batch of events"""
        parsed_events = []
        
        for raw_event in raw_events:
            try:
                # Parse raw log
                event = json.loads(raw_event)
                
                # Parse and normalize
                parsed = self.parser_engine.parse(event)
                
                if parsed:
                    # Map to ECS format
                    ecs_event = self.ecs_mapper.map(parsed)
                    
                    # Enrich
                    enriched_event = self._enrich_event(ecs_event)
                    
                    # Apply detection rules
                    self._apply_rules(enriched_event)
                    
                    parsed_events.append(enriched_event)
                    self.metrics["events_processed"] += 1
                else:
                    self.metrics["parse_errors"] += 1
                    
            except Exception as e:
                self.logger.error("Event processing error", error=str(e))
                self.metrics["parse_errors"] += 1
        
        # Bulk index to OpenSearch
        if parsed_events:
            self._index_events(parsed_events)
    
    def _enrich_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich event with additional data"""
        enriched = event.copy()
        
        for enricher in self.enrichers:
            try:
                enriched = enricher.enrich(enriched)
            except Exception as e:
                self.logger.warning(
                    "Enrichment failed",
                    enricher=enricher.__class__.__name__,
                    error=str(e)
                )
        
        self.metrics["events_enriched"] += 1
        return enriched
    
    def _apply_rules(self, event: Dict[str, Any]):
        """Apply detection rules to event"""
        for rule in self.rules:
            if not rule.get("enabled", True):
                continue
            
            try:
                # Check if rule matches
                if self._rule_matches(rule, event):
                    self.metrics["rules_matched"] += 1
                    
                    # Handle different rule types
                    rule_type = rule.get("type", "simple")
                    
                    if rule_type == "threshold":
                        # Track threshold
                        if self.threshold_tracker.check(rule, event):
                            self._generate_alert(rule, event)
                    
                    elif rule_type == "correlation":
                        # Track correlation
                        if self.correlation_engine.check(rule, event):
                            self._generate_alert(rule, event)
                    
                    else:
                        # Simple match
                        self._generate_alert(rule, event)
                        
            except Exception as e:
                self.logger.error(
                    "Rule evaluation error",
                    rule=rule.get("name"),
                    error=str(e)
                )
    
    def _rule_matches(self, rule: Dict[str, Any], event: Dict[str, Any]) -> bool:
        """Check if rule matches event"""
        detection = rule.get("detection", {})
        selection = detection.get("selection", {})
        
        # Check all selection criteria
        for field, value in selection.items():
            event_value = self._get_nested_value(event, field)
            
            if isinstance(value, list):
                if event_value not in value:
                    return False
            elif isinstance(value, dict):
                # Handle operators like gte, lte, contains
                if not self._check_condition(event_value, value):
                    return False
            else:
                if event_value != value:
                    return False
        
        return True
    
    def _get_nested_value(self, obj: Dict, key: str) -> Any:
        """Get nested dictionary value using dot notation"""
        keys = key.split(".")
        value = obj
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return None
        
        return value
    
    def _check_condition(self, value: Any, condition: Dict) -> bool:
        """Check value against condition operators"""
        for op, target in condition.items():
            if op == "gte" and value < target:
                return False
            elif op == "lte" and value > target:
                return False
            elif op == "gt" and value <= target:
                return False
            elif op == "lt" and value >= target:
                return False
            elif op == "contains" and target not in str(value):
                return False
            elif op == "regex":
                import re
                if not re.search(target, str(value)):
                    return False
        
        return True
    
    def _generate_alert(self, rule: Dict[str, Any], event: Dict[str, Any]):
        """Generate alert from rule match"""
        alert = {
            "@timestamp": datetime.utcnow().isoformat(),
            "rule": {
                "id": rule.get("id"),
                "name": rule.get("name"),
                "description": rule.get("description"),
                "severity": rule.get("severity", "MEDIUM"),
                "category": rule.get("category")
            },
            "event": event,
            "alert": {
                "status": "new",
                "generated_at": datetime.utcnow().isoformat()
            }
        }
        
        # Push to alert queue
        self.redis_client.lpush("alerts:queue", json.dumps(alert))
        self.metrics["alerts_generated"] += 1
        
        self.logger.info(
            "Alert generated",
            rule=rule.get("name"),
            severity=rule.get("severity")
        )
    
    def _index_events(self, events: List[Dict[str, Any]]):
        """Bulk index events to OpenSearch"""
        import os
        index_name = os.getenv("INDEX_EVENTS", "siem-events")
        
        try:
            # Prepare bulk actions
            actions = [
                {
                    "_index": f"{index_name}-{datetime.utcnow().strftime('%Y.%m.%d')}",
                    "_source": event
                }
                for event in events
            ]
            
            # Bulk index
            helpers.bulk(self.opensearch, actions)
            
            self.logger.debug(
                "Events indexed",
                count=len(events),
                index=index_name
            )
            
        except Exception as e:
            self.logger.error("Failed to index events", error=str(e))
    
    def _rule_reload_worker(self):
        """Periodically reload rules"""
        import os
        reload_interval = int(os.getenv("RULE_RELOAD_INTERVAL", 60))
        
        while self.running:
            time.sleep(reload_interval)
            
            try:
                new_rules = self.rule_loader.load_all_rules()
                self.rules = new_rules
                self.logger.info("Rules reloaded", count=len(new_rules))
            except Exception as e:
                self.logger.error("Failed to reload rules", error=str(e))
