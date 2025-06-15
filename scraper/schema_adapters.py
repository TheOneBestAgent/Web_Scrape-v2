"""Simple data schema adapters."""
from typing import List, Dict, Any


def adapt_auction_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Adapt raw item dicts to a standard schema."""
    adapted = []
    for item in items:
        adapted.append({
            "title": item.get("title"),
            "price": item.get("price"),
            "end_time": item.get("end_time"),
            "image": item.get("image_url"),
            "url": item.get("item_url"),
        })
    return adapted
