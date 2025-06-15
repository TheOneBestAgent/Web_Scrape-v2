# scraper/core.py

from scraper.config_manager import get_config_for_domain
from scraper.selector_logger import update_successful_selectors
from scraper.config_sync import sync_config_to_db
from scraper.heuristics_logger import log_heuristics
from scraper.extractor import Extractor
from scraper.selector_manager import get_valid_auction_selectors
from utils.memory import MemoryBank
from utils.logger import Logger
from urllib.parse import urlparse
from time import time
from playwright.async_api import async_playwright
import os
from datetime import datetime
import json
import asyncio

class Scraper:
    def __init__(self, url, memory: MemoryBank | None = None, logger: Logger | None = None):
        self.url = url if url.startswith(('http://', 'https://')) else f'https://{url}'
        self.domain = urlparse(self.url).netloc
        self.config_path = f"config/sites/{self.domain}.yaml"
        self.config = get_config_for_domain(self.url)

        self.memory = memory or MemoryBank(self.domain)
        self.logger = logger or Logger(self.domain)

        self.enable_dynamic = self.config.get("enable_dynamic", True)
        self.enable_navigation = self.config.get("enable_navigation", True)
        self.enable_auction = self.config.get("enable_auction", True)
        self.custom_selectors = self.config.get("custom_selectors", {})


    async def load_html(self):
        """Load HTML content using Playwright."""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            try:
                self.logger.info("Loading page...")
                await page.goto(self.url, wait_until='networkidle')
                
                self.logger.info("Waiting for initial content...")
                await page.wait_for_load_state('domcontentloaded')
                
                if self.enable_dynamic:
                    self.logger.info("Scrolling to load more content...")
                    await page.evaluate("""
                        window.scrollTo(0, document.body.scrollHeight);
                        setTimeout(() => { window.scrollTo(0, 0); }, 2000);
                    """)
                    
                    self.logger.info("Waiting for dynamic content...")
                    try:
                        await page.wait_for_selector("div[class*='lot'], .auction-item, [data-lot-id]", timeout=30000)
                        self.logger.info("Found content with selector: div[class*='lot']")
                    except Exception as e:
                        self.logger.warning(f"Timeout waiting for auction items: {str(e)}")
                
                return await page.content(), page
            finally:
                await browser.close()

    async def run(self):
        """Main scraping method."""
        try:
            t1 = time()
            self.logger.info(f"Starting scrape of {self.url}")
            
            html, page = await self.load_html()

            selectors = get_valid_auction_selectors(html, self.custom_selectors.get("auction_items"))
            extractor = Extractor(html, self.url, {"auction_items": selectors})
            extracted_data = await extractor.extract()

            t2 = time()

            if "auction_items" in self.custom_selectors:
                update_successful_selectors(self.url, "auction_items", self.custom_selectors["auction_items"])

            sync_config_to_db(self.config_path)

            log_heuristics(self.url, {
                "dynamic_enabled": self.enable_dynamic,
                "selector_types": list(self.custom_selectors.keys()),
                "timing": {
                    "start": t1,
                    "end": t2,
                    "duration_sec": round(t2 - t1, 2)
                }
            })

            self.save_data(extracted_data)
            self.logger.info("Scrape completed successfully")
            
            return extracted_data
        except Exception as e:
            self.logger.error(f"Error during scraping: {str(e)}")
            self.record_error(str(e))
            raise

    def save_data(self, data):
        """Save extracted data to JSON files."""
        memory_dir = os.path.join('memory', self.domain)
        os.makedirs(memory_dir, exist_ok=True)
        
        # Save main data
        with open(os.path.join(memory_dir, 'extracted_data.json'), 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Save metadata
        metadata = {
            'url': self.url,
            'domain': self.domain,
            'scrape_time': datetime.utcnow().isoformat(),
            'version': '1.0'
        }
        with open(os.path.join(memory_dir, 'metadata.json'), 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
    def record_error(self, error_message):
        """Record error in error history file."""
        error_file = os.path.join('memory', self.domain, 'error_history.json')
        errors = []
        
        if os.path.exists(error_file):
            try:
                with open(error_file, 'r', encoding='utf-8') as f:
                    errors = json.load(f)
            except json.JSONDecodeError:
                errors = []
        
        errors.append({
            'timestamp': datetime.utcnow().isoformat(),
            'error': error_message
        })
        
        with open(error_file, 'w', encoding='utf-8') as f:
            json.dump(errors, f, indent=2, ensure_ascii=False)

