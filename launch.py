#!/usr/bin/env python3

import sys
import asyncio
from scraper.core import Scraper

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 launch.py <url>")
        sys.exit(1)
        
    url = sys.argv[1]
    scraper = Scraper(url)
    
    try:
        asyncio.run(scraper.run())
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
