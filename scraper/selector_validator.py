"""Validation utilities for CSS selectors."""
from bs4 import BeautifulSoup
from typing import Iterable, List


def validate_selectors(html: str, selectors: Iterable[str]) -> List[str]:
    """Return selectors that match at least one element."""
    soup = BeautifulSoup(html, "html.parser")
    valid: List[str] = []
    for sel in selectors:
        if soup.select_one(sel):
            valid.append(sel)
    return valid
