# cursor_scraper_template/main.py

import asyncio
from scraper.core import Scraper


async def main():
    url = input("Enter target URL: ")

    scraper = Scraper(url=url)

    try:
        await scraper.run()
    except Exception as e:
        print(f"[FATAL] Scraper failed with error: {e}")

if __name__ == '__main__':
    asyncio.run(main())
