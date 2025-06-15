"""Manage selector discovery and validation."""
from typing import List, Iterable

from .selector_generator import generate_auction_selectors
from .selector_validator import validate_selectors


def get_valid_auction_selectors(html: str, custom: Iterable[str] | None = None) -> List[str]:
    """Return validated selectors for auction items."""
    candidates = list(custom) if custom else generate_auction_selectors(html)
    return validate_selectors(html, candidates)
