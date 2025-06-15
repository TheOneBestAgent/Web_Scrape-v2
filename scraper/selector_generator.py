"""Generate fallback CSS selectors based on page content."""
from bs4 import BeautifulSoup
from typing import List

DEFAULT_AUCTION_SELECTORS = [
    "div[class*='lot']",
    "div[class*='auction-item']",
    "div[data-lot-id]",
    "div[class*='product']",
]


def generate_auction_selectors(html: str) -> List[str]:
    """Return a list of possible auction item selectors in order of likelihood."""
    soup = BeautifulSoup(html, "html.parser")
    results: List[str] = []
    for sel in DEFAULT_AUCTION_SELECTORS:
        if soup.select_one(sel):
            results.append(sel)
    return results or DEFAULT_AUCTION_SELECTORS
