# scraper/config_manager.py

import os
import yaml
from urllib.parse import urlparse

def get_config_for_domain(url):
    """Get configuration for a specific domain."""
    domain = urlparse(url).netloc
    config_path = f"config/sites/{domain}.yaml"
    
    # Create config directory if it doesn't exist
    os.makedirs("config/sites", exist_ok=True)
    
    # Load existing config or create default
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    else:
        # Create default config
        default_config = {
            "enable_dynamic": True,
            "enable_navigation": True,
            "enable_auction": True,
            "custom_selectors": {
                "auction_items": [
                    "div[class*='lot']",
                    "div[class*='auction-item']",
                    "div[class*='product']",
                    "div[data-lot-id]"
                ]
            },
            "api_endpoints": [],
            "timeouts": {
                "page_load": 30,
                "dynamic_wait": 5
            },
            "retry_attempts": 3,
            "scroll": True,
            "scroll_step": 500,
            "scroll_delay": 0.1
        }
        
        # Save default config
        with open(config_path, 'w') as f:
            yaml.dump(default_config, f)
        
        return default_config
