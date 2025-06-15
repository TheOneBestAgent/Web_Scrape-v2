"""Utilities for repairing or rotating selectors."""
import logging
from typing import Callable, Iterable, Tuple, Any

logger = logging.getLogger(__name__)


def rotate_and_retry_selectors(
    selectors: Iterable[str],
    extract_fn: Callable[[str, str], Any],
    html: str,
    url: str,
) -> Tuple[str, Any]:
    """Try each selector until extraction succeeds."""
    for sel in selectors:
        try:
            data = extract_fn(sel, html)
            if data:
                logger.info("Selector '%s' succeeded", sel)
                return sel, data
        except Exception as exc:
            logger.debug("Selector '%s' failed: %s", sel, exc)
    raise ValueError(f"No valid selector found for {url}")
