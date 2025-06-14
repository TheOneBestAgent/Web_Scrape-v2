# scraper/heuristics_logger.py

import os
import json
from datetime import datetime
from urllib.parse import urlparse

def log_heuristics(url, data):
    """Log scraping heuristics for analysis."""
    domain = urlparse(url).netloc
    log_dir = os.path.join('memory', domain, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, 'heuristics.json')
    
    # Initialize data structure
    log_data = {
        'last_updated': datetime.utcnow().isoformat(),
        'scrapes': []
    }
    
    # Load existing data if available
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
        except json.JSONDecodeError:
            pass
    
    # Add new scrape data
    log_data['scrapes'].append({
        'timestamp': datetime.utcnow().isoformat(),
        'data': data
    })
    
    # Keep only last 100 scrapes
    log_data['scrapes'] = log_data['scrapes'][-100:]
    log_data['last_updated'] = datetime.utcnow().isoformat()
    
    # Save updated data
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)

# Example usage from within core or extractor (you'd call this with something like):
# log_heuristics(url, {
#     "dynamic_scrolls": 3,
#     "xhr_patterns": ["/api/items", "/lots.json"],
#     "selector_hits": {".lot-card": true, ".item-block": false},
#     "timing": {"start": t1, "end": t2, "duration_sec": t2 - t1}
# })
