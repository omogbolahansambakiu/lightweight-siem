#!/usr/bin/env python3
"""
Detection Engine - Main Entry Point

This is the core processing engine that:
1. Pulls raw events from Redis queue
2. Parses and normalizes logs to ECS format
3. Enriches with GeoIP, DNS, and threat intel
4. Applies detection rules
5. Generates alerts and stores events
"""

import os
import sys
import signal
import time
import logging
from typing import List
import structlog
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.detection_engine import DetectionEngine
from parsers.parser_engine import ParserEngine
from enrichment.geoip import GeoIPEnricher
from enrichment.dns import DNSEnricher
from enrichment.threat_intel import ThreatIntelEnricher
from utils.ecs_mapper import ECSMapper

# Load environment variables
load_dotenv()

# Configure logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


class SIEMDetectionEngine:
    """Main SIEM Detection Engine orchestrator"""
    
    def __init__(self):
        self.running = False
        self.logger = logger.bind(component="detection-engine")
        
        # Initialize components
        self.logger.info("Initializing Detection Engine components...")
        
        try:
            # Parser Engine
            self.parser_engine = ParserEngine()
            
            # Enrichers
            self.geoip_enricher = GeoIPEnricher()
            self.dns_enricher = DNSEnricher()
            self.threat_intel_enricher = ThreatIntelEnricher()
            
            # ECS Mapper
            self.ecs_mapper = ECSMapper()
            
            # Detection Engine
            self.detection_engine = DetectionEngine(
                parser_engine=self.parser_engine,
                enrichers=[
                    self.geoip_enricher,
                    self.dns_enricher,
                    self.threat_intel_enricher
                ],
                ecs_mapper=self.ecs_mapper
            )
            
            self.logger.info("All components initialized successfully")
            
        except Exception as e:
            self.logger.error("Failed to initialize components", error=str(e))
            raise
    
    def start(self):
        """Start the detection engine"""
        self.logger.info("Starting Detection Engine...")
        self.running = True
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        try:
            # Start the detection engine
            self.detection_engine.start()
            
            # Keep main thread alive
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        except Exception as e:
            self.logger.error("Fatal error in detection engine", error=str(e))
            raise
        finally:
            self.stop()
    
    def stop(self):
        """Stop the detection engine gracefully"""
        self.logger.info("Stopping Detection Engine...")
        self.running = False
        
        try:
            self.detection_engine.stop()
            self.logger.info("Detection Engine stopped successfully")
        except Exception as e:
            self.logger.error("Error during shutdown", error=str(e))
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info("Received signal", signal=signum)
        self.running = False


def main():
    """Main entry point"""
    logger.info("=" * 60)
    logger.info("SIEM Detection Engine v1.0.0")
    logger.info("=" * 60)
    
    # Validate environment
    required_env_vars = [
        "OPENSEARCH_HOST",
        "REDIS_HOST"
    ]
    
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(
            "Missing required environment variables",
            missing=missing_vars
        )
        sys.exit(1)
    
    # Create and start engine
    try:
        engine = SIEMDetectionEngine()
        engine.start()
    except Exception as e:
        logger.error("Failed to start detection engine", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
