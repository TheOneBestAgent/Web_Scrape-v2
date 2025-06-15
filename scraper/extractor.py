# scraper/extractor.py

from bs4 import BeautifulSoup
import json
from datetime import datetime
import logging
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin, urlparse


class Extractor:
    """Extracts auction and navigation data from HTML pages."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    async def extract(
        self,
        html: str,
        url: str,
        page=None,
        override_selector: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Extract all relevant data from a page."""
        self.html = html
        self.url = url
        self.soup = BeautifulSoup(html, "html.parser")

        data = {
            "url": url,
            "timestamp": datetime.utcnow().isoformat(),
            "auction_data": [],
            "navigation": {},
            "metadata": {},
        }

        if self._has_auction_data(override_selector):
            data["auction_data"] = await self._extract_auction_data(override_selector)

        if self._has_navigation():
            data["navigation"] = self._extract_navigation()

        data["metadata"] = self._extract_metadata()
        return data

    def _has_auction_data(self, override_selector: Optional[str]) -> bool:
        selectors = [
            override_selector,
            "div[class*='lot']",
            "div[class*='auction-item']",
            "div[class*='product']",
            "div[data-lot-id]",
        ]
        for selector in selectors:
            if selector and self.soup.select_one(selector):
                return True
        return False

    def _has_navigation(self) -> bool:
        selectors = [
            "nav",
            "ul[class*='pagination']",
            "div[class*='pagination']",
            "a[class*='next']",
            "a[class*='prev']",
        ]
        for selector in selectors:
            if self.soup.select_one(selector):
                return True
        return False

    async def _extract_auction_data(self, override_selector: Optional[str]) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        selectors = [
            override_selector,
            "div[class*='lot']",
            "div[class*='auction-item']",
            "div[class*='product']",
            "div[data-lot-id]",
        ]
        for selector in selectors:
            if not selector:
                continue
            elements = self.soup.select(selector)
            if elements:
                for element in elements:
                    item = self._extract_item_data(element)
                    if item:
                        items.append(item)
                if items:
                    break
        return items

    def _extract_item_data(self, element) -> Optional[Dict[str, Any]]:
        try:
            title = self._safe_extract_text(
                element,
                ["h1", "h2", "h3", "h4", "div[class*='title']", "div[class*='name']"],
            )
            price = self._safe_extract_text(
                element,
                ["span[class*='price']", "div[class*='price']", "span[class*='amount']"],
            )
            end_time = self._safe_extract_text(
                element,
                ["div[class*='end-time']", "div[class*='countdown']", "span[class*='time']"],
            )
            img_url = self._safe_extract_attr(element, "img", "src")
            if img_url:
                img_url = urljoin(self.url, img_url)
            item_url = self._safe_extract_attr(element, "a", "href")
            if item_url:
                item_url = urljoin(self.url, item_url)
            return {
                "title": title,
                "price": price,
                "end_time": end_time,
                "image_url": img_url,
                "item_url": item_url,
                "selector": element.name
                + "".join(f"[{k}='{v}']" for k, v in element.attrs.items()),
            }
        except Exception as e:  # noqa: PERF203
            self.logger.error(f"Error extracting item data: {e}")
            return None

    def _extract_navigation(self) -> Dict[str, Any]:
        nav_data = {
            "next_page": None,
            "prev_page": None,
            "current_page": 1,
            "total_pages": None,
        }
        next_link = self.soup.select_one("a[class*='next']")
        if next_link and "href" in next_link.attrs:
            nav_data["next_page"] = urljoin(self.url, next_link["href"])
        prev_link = self.soup.select_one("a[class*='prev']")
        if prev_link and "href" in prev_link.attrs:
            nav_data["prev_page"] = urljoin(self.url, prev_link["href"])
        current_page = self.soup.select_one("span[class*='current']")
        if current_page:
            try:
                nav_data["current_page"] = int(current_page.text.strip())
            except ValueError:
                pass
        total_pages = self.soup.select_one("span[class*='total']")
        if total_pages:
            try:
                nav_data["total_pages"] = int(total_pages.text.strip())
            except ValueError:
                pass
        return nav_data

    def _extract_metadata(self) -> Dict[str, Any]:
        metadata = {
            "title": self._safe_extract_text(self.soup, ["title"]),
            "description": self._safe_extract_attr(
                self.soup, "meta[name='description']", "content"
            ),
            "keywords": self._safe_extract_attr(
                self.soup, "meta[name='keywords']", "content"
            ),
            "canonical_url": self._safe_extract_attr(
                self.soup, "link[rel='canonical']", "href"
            ),
            "domain": urlparse(self.url).netloc,
        }
        structured_data = self._extract_structured_data()
        if structured_data:
            metadata["structured_data"] = structured_data
        return metadata

    def _extract_structured_data(self) -> Optional[Dict[str, Any]]:
        json_ld = self.soup.select_one("script[type='application/ld+json']")
        if json_ld:
            try:
                return json.loads(json_ld.string)
            except (json.JSONDecodeError, TypeError):
                pass
        microdata: Dict[str, Any] = {}
        for item in self.soup.select("[itemtype]"):
            item_type = item.get("itemtype", "").split("/")[-1]
            item_props = {}
            for prop in item.select("[itemprop]"):
                prop_name = prop.get("itemprop")
                prop_value = prop.get("content") or prop.text.strip()
                item_props[prop_name] = prop_value
            if item_props:
                microdata[item_type] = item_props
        return microdata or None

    def _safe_extract_text(self, element, selectors: List[str]) -> Optional[str]:
        for selector in selectors:
            found = element.select_one(selector)
            if found and found.text.strip():
                return found.text.strip()
        return None

    def _safe_extract_attr(self, element, selector: str, attr: str) -> Optional[str]:
        found = element.select_one(selector)
        if found and attr in found.attrs:
            return found[attr]
        return None
