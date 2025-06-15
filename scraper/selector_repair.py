"""Utility helpers for rotating through selector options."""
from typing import Callable, Iterable, Tuple, Any, Awaitable
import asyncio


async def rotate_and_retry_selectors(
    selectors: Iterable[str],
    extract_fn: Callable[[str, str], Awaitable[Any]],
    html: str,
    url: str,
) -> Tuple[str, Any]:
    """Try each selector until extraction succeeds."""
    last_error: Exception | None = None
    for sel in selectors:
        try:
            result = await extract_fn(sel, html)
            if result:
                return sel, result
        except Exception as e:  # noqa: PERF203
            last_error = e
    raise RuntimeError(f"All selectors failed for {url}. Last error: {last_error}")
