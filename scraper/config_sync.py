# scraper/config_sync.py

import os
import yaml
import json
from datetime import datetime

def sync_config_to_db(config_path):
    """Sync configuration to database (currently JSON file)."""
    if not os.path.exists(config_path):
        return
    
    # Load config
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    # Create sync directory
    sync_dir = os.path.join("memory", "config_sync")
    os.makedirs(sync_dir, exist_ok=True)
    
    # Save to JSON
    sync_file = os.path.join(sync_dir, os.path.basename(config_path).replace(".yaml", ".json"))
    with open(sync_file, "w", encoding="utf-8") as f:
        json.dump({
            "config": config,
            "last_sync": datetime.utcnow().isoformat(),
            "source_path": config_path
        }, f, indent=2, ensure_ascii=False)