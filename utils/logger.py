import logging
import os
from datetime import datetime

class Logger:
    def __init__(self, domain: str = "global"):
        self.domain = domain or "global"
        log_dir = os.path.join("logs", self.domain)
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"{self.domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(self.domain)

    def log_info(self, message: str):
        self.logger.info(message)

    def log_error(self, message: str, error: str | None = None):
        if error:
            self.logger.error(f"{message}: {error}")
        else:
            self.logger.error(message)
