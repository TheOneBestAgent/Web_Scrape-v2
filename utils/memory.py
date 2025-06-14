# utils/memory.py

import os
import json
from urllib.parse import urlparse
from datetime import datetime

class MemoryBank:
    def __init__(self, domain):
        self.domain = urlparse(domain).netloc.replace("www.", "")
        self.dir = os.path.join("memory", self.domain)
        os.makedirs(self.dir, exist_ok=True)

        self.data_file = os.path.join(self.dir, "extracted_data.json")
        self.fail_file = os.path.join(self.dir, "error_history.json")
        self.pattern_file = os.path.join(self.dir, "learned_selectors.json")
        self.metadata_file = os.path.join(self.dir, "metadata.json")

        # Load or initialize memory structures
        self.data = self._load_json(self.data_file, [])
        self.failures = self._load_json(self.fail_file, [])
        self.patterns = self._load_json(self.pattern_file, {})
        self.metadata = self._load_json(self.metadata_file, {
            "last_scraped": None,
            "retry_queue": [],
            "successful_pages": 0,
            "failed_pages": 0
        })

    def _load_json(self, path, default):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return default

    def _save_json(self, path, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def save_data(self, page_data):
        self.data.append(page_data)
        self.metadata["successful_pages"] += 1
        self.metadata["last_scraped"] = datetime.utcnow().isoformat()
        self._save_json(self.data_file, self.data)
        self._save_json(self.metadata_file, self.metadata)

    def save_failure(self, error_type, error_message):
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "error_type": error_type,
            "message": error_message
        }
        self.failures.append(record)
        self.metadata["failed_pages"] += 1
        self._save_json(self.fail_file, self.failures)
        self._save_json(self.metadata_file, self.metadata)

    def learn_selector(self, field, selector):
        if field not in self.patterns:
            self.patterns[field] = []
        if selector not in self.patterns[field]:
            self.patterns[field].append(selector)
        self._save_json(self.pattern_file, self.patterns)

    def queue_retry(self, url):
        if url not in self.metadata["retry_queue"]:
            self.metadata["retry_queue"].append(url)
            self._save_json(self.metadata_file, self.metadata)

    def get_retry_queue(self):
        return self.metadata.get("retry_queue", [])

    def dequeue_retry(self, url):
        if url in self.metadata["retry_queue"]:
            self.metadata["retry_queue"].remove(url)
            self._save_json(self.metadata_file, self.metadata)
