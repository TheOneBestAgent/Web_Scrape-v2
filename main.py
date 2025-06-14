# cursor_scraper_template/main.py

import asyncio
from scraper.core import Scraper
from utils.memory import MemoryBank
from utils.logger import Logger

async def main():
    url = input("Enter target URL: ")

    memory = MemoryBank(domain=url)
    logger = Logger(domain=url)

    scraper = Scraper(
        url=url,
        memory=memory,
        logger=logger
    )

    try:
        await scraper.run()
    except Exception as e:
        logger.log_error("Unhandled exception", str(e))
        print(f"[FATAL] Scraper failed with error: {e}")

if __name__ == '__main__':
    asyncio.run(main())
