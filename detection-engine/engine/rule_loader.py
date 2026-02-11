"""Rule Loader - Loads and manages detection rules"""
import os
import yaml
import glob
from typing import List, Dict, Any
import structlog

logger = structlog.get_logger()

class RuleLoader:
    """Loads and validates detection rules from YAML files"""
    
    def __init__(self, rules_dir="/app/rules"):
        self.rules_dir = rules_dir
        self.logger = logger.bind(component="rule-loader")
    
    def load_all_rules(self) -> List[Dict[str, Any]]:
        """Load all rules from rules directory"""
        rules = []
        
        # Find all YAML files
        pattern = os.path.join(self.rules_dir, "**/*.yml")
        rule_files = glob.glob(pattern, recursive=True)
        
        for rule_file in rule_files:
            try:
                with open(rule_file, 'r') as f:
                    rule = yaml.safe_load(f)
                    
                    if rule and self._validate_rule(rule):
                        rule['file'] = rule_file
                        rules.append(rule)
                    else:
                        self.logger.warning("Invalid rule", file=rule_file)
                        
            except Exception as e:
                self.logger.error("Failed to load rule", file=rule_file, error=str(e))
        
        self.logger.info("Rules loaded", count=len(rules))
        return rules
    
    def _validate_rule(self, rule: Dict[str, Any]) -> bool:
        """Validate rule structure"""
        required_fields = ['name', 'description', 'severity', 'detection']
        
        for field in required_fields:
            if field not in rule:
                return False
        
        return True
