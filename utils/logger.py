import os
import logging
from datetime import datetime
from urllib.parse import urlparse

class Logger:
    """Simple logger that writes to both console and file."""

    def __init__(self, domain: str = "global"):
        domain = urlparse(domain).netloc or domain
        log_dir = os.path.join("memory", domain, "logs")
        os.makedirs(log_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"scraper_{timestamp}.log")

        self.logger = logging.getLogger(domain)
        self.logger.setLevel(logging.INFO)

        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        fh = logging.FileHandler(log_file)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        self.logger.addHandler(sh)

    def info(self, msg: str):
        self.logger.info(msg)

    def error(self, msg: str):
        self.logger.error(msg)

    def debug(self, msg: str):
        self.logger.debug(msg)

    def log_error(self, context: str, message: str):
        self.error(f"{context}: {message}")
