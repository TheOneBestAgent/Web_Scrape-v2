# scraper/extractor.py

from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import logging
from typing import Dict, Any, Optional, List, Tuple
from urllib.parse import urljoin, urlparse

class Extractor:
    def __init__(self, html: str, url: str, custom_selectors: Dict[str, List[str]] | None = None):
        self.html = html
        self.url = url
        self.soup = BeautifulSoup(html, 'html.parser')
        self.logger = logging.getLogger(__name__)
        self.custom_selectors = custom_selectors or {}

    async def extract(self) -> Dict[str, Any]:
        """
        Extract all data from the page.
        
        Returns:
            Dictionary containing extracted data
        """
        data = {
            'url': self.url,
            'timestamp': datetime.utcnow().isoformat(),
            'auction_data': [],
            'navigation': {},
            'metadata': {}
        }

        # Extract auction data
        if self._has_auction_data():
            data['auction_data'] = await self._extract_auction_data()

        # Extract navigation
        if self._has_navigation():
            data['navigation'] = self._extract_navigation()

        # Extract metadata
        data['metadata'] = self._extract_metadata()

        return data

    def _has_auction_data(self) -> bool:
        """Check if page contains auction data."""
        # Look for common auction item selectors
        selectors = self.custom_selectors.get('auction_items', [
            'div[class*="lot"]',
            'div[class*="auction-item"]',
            'div[class*="product"]',
            'div[data-lot-id]'
        ])
        
        for selector in selectors:
            if self.soup.select_one(selector):
                return True
        return False

    def _has_navigation(self) -> bool:
        """Check if page contains navigation elements."""
        # Look for common navigation selectors
        selectors = self.custom_selectors.get('navigation', [
            'nav',
            'ul[class*="pagination"]',
            'div[class*="pagination"]',
            'a[class*="next"]',
            'a[class*="prev"]'
        ])
        
        for selector in selectors:
            if self.soup.select_one(selector):
                return True
        return False

    async def _extract_auction_data(self) -> List[Dict[str, Any]]:
        """
        Extract auction item data.
        
        Returns:
            List of dictionaries containing auction item data
        """
        items = []
        
        # Try different selectors for auction items
        selectors = self.custom_selectors.get('auction_items', [
            'div[class*="lot"]',
            'div[class*="auction-item"]',
            'div[class*="product"]',
            'div[data-lot-id]'
        ])
        
        for selector in selectors:
            elements = self.soup.select(selector)
            if elements:
                for element in elements:
                    item = self._extract_item_data(element)
                    if item:
                        items.append(item)
                break
        
        return items

    def _extract_item_data(self, element) -> Optional[Dict[str, Any]]:
        """
        Extract data from an auction item element.
        
        Args:
            element: BeautifulSoup element containing item data
            
        Returns:
            Dictionary containing item data or None if extraction fails
        """
        try:
            # Extract title
            title = self._safe_extract_text(element, [
                'h1', 'h2', 'h3', 'h4',
                'div[class*="title"]',
                'div[class*="name"]'
            ])
            
            # Extract price
            price = self._safe_extract_text(element, [
                'span[class*="price"]',
                'div[class*="price"]',
                'span[class*="amount"]'
            ])
            
            # Extract end time
            end_time = self._safe_extract_text(element, [
                'div[class*="end-time"]',
                'div[class*="countdown"]',
                'span[class*="time"]'
            ])
            
            # Extract image URL
            img_url = self._safe_extract_attr(element, 'img', 'src')
            if img_url:
                img_url = urljoin(self.url, img_url)
            
            # Extract item URL
            item_url = self._safe_extract_attr(element, 'a', 'href')
            if item_url:
                item_url = urljoin(self.url, item_url)
            
            return {
                'title': title,
                'price': price,
                'end_time': end_time,
                'image_url': img_url,
                'item_url': item_url,
                'selector': element.name + ''.join(f'[{k}="{v}"]' for k, v in element.attrs.items())
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting item data: {str(e)}")
            return None

    def _extract_navigation(self) -> Dict[str, Any]:
        """
        Extract navigation data.
        
        Returns:
            Dictionary containing navigation data
        """
        nav_data = {
            'next_page': None,
            'prev_page': None,
            'current_page': 1,
            'total_pages': None
        }
        
        # Extract next page URL
        pagination_selectors = self.custom_selectors.get('pagination', ['a[class*="next"]', 'a[class*="prev"]'])
        next_link = self.soup.select_one(pagination_selectors[0])
        if next_link and 'href' in next_link.attrs:
            nav_data['next_page'] = urljoin(self.url, next_link['href'])
        
        # Extract previous page URL
        prev_link = self.soup.select_one(pagination_selectors[-1])
        if prev_link and 'href' in prev_link.attrs:
            nav_data['prev_page'] = urljoin(self.url, prev_link['href'])
        
        # Extract current page number
        current_page = self.soup.select_one('span[class*="current"]')
        if current_page:
            try:
                nav_data['current_page'] = int(current_page.text.strip())
            except ValueError:
                pass
        
        # Extract total pages
        total_pages = self.soup.select_one('span[class*="total"]')
        if total_pages:
            try:
                nav_data['total_pages'] = int(total_pages.text.strip())
            except ValueError:
                pass
        
        return nav_data

    def _extract_metadata(self) -> Dict[str, Any]:
        """
        Extract page metadata.
        
        Returns:
            Dictionary containing metadata
        """
        metadata = {
            'title': self._safe_extract_text(self.soup, ['title']),
            'description': self._safe_extract_attr(self.soup, 'meta[name="description"]', 'content'),
            'keywords': self._safe_extract_attr(self.soup, 'meta[name="keywords"]', 'content'),
            'canonical_url': self._safe_extract_attr(self.soup, 'link[rel="canonical"]', 'href'),
            'domain': urlparse(self.url).netloc
        }
        
        # Extract structured data
        structured_data = self._extract_structured_data()
        if structured_data:
            metadata['structured_data'] = structured_data
        
        return metadata

    def _extract_structured_data(self) -> Optional[Dict[str, Any]]:
        """
        Extract structured data from JSON-LD or microdata.
        
        Returns:
            Dictionary containing structured data or None if not found
        """
        # Try JSON-LD
        json_ld = self.soup.select_one('script[type="application/ld+json"]')
        if json_ld:
            try:
                return json.loads(json_ld.string)
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Try microdata
        microdata = {}
        for item in self.soup.select('[itemtype]'):
            item_type = item.get('itemtype', '').split('/')[-1]
            item_props = {}
            
            for prop in item.select('[itemprop]'):
                prop_name = prop.get('itemprop')
                prop_value = prop.get('content') or prop.text.strip()
                item_props[prop_name] = prop_value
            
            if item_props:
                microdata[item_type] = item_props
        
        return microdata if microdata else None

    def _safe_extract_text(self, element, selectors: List[str]) -> Optional[str]:
        """
        Safely extract text from element using selectors.
        
        Args:
            element: BeautifulSoup element to search in
            selectors: List of CSS selectors to try
            
        Returns:
            Extracted text or None if not found
        """
        for selector in selectors:
            found = element.select_one(selector)
            if found and found.text.strip():
                return found.text.strip()
        return None

    def _safe_extract_attr(self, element, selector: str, attr: str) -> Optional[str]:
        """
        Safely extract attribute from element using selector.
        
        Args:
            element: BeautifulSoup element to search in
            selector: CSS selector to use
            attr: Attribute name to extract
            
        Returns:
            Attribute value or None if not found
        """
        found = element.select_one(selector)
        if found and attr in found.attrs:
            return found[attr]
        return None
