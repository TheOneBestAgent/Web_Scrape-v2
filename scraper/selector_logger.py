# scraper/selector_logger.py

import os
import json
from datetime import datetime
from urllib.parse import urlparse

def update_successful_selectors(url, selector_type, selectors):
    """Update successful selectors for a domain."""
    domain = urlparse(url).netloc
    log_dir = os.path.join('memory', domain, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, 'successful_selectors.json')
    
    # Initialize data structure
    data = {
        'last_updated': datetime.utcnow().isoformat(),
        'selectors': {}
    }
    
    # Load existing data if available
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            pass
    
    # Update selectors
    data['selectors'][selector_type] = selectors
    data['last_updated'] = datetime.utcnow().isoformat()
    
    # Save updated data
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
