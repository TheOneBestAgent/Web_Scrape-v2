# scraper/render_engine.py

from playwright.async_api import async_playwright
import asyncio

class Renderer:
    def __init__(self):
        self.browser = None

    async def load(self, url):
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--ignore-certificate-errors', '--no-sandbox']
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
                locale="en-US",
                viewport={"width": 1280, "height": 800},
                java_script_enabled=True,
                bypass_csp=True,
                ignore_https_errors=True
            )
            page = await context.new_page()

            try:
                # Set up request interception
                await page.route("**/*", lambda route: asyncio.create_task(self._handle_route(route)))
                
                # Navigate with increased timeout
                await page.goto(url, timeout=60000, wait_until='networkidle')
                
                # Wait for content to load
                await page.wait_for_load_state('domcontentloaded')
                await page.wait_for_load_state('networkidle')
                
                # Scroll behavior
                await page.evaluate("""
                    () => {
                        window.scrollTo(0, 0);
                        const scrollHeight = document.body.scrollHeight;
                        const viewportHeight = window.innerHeight;
                        for (let i = 0; i < scrollHeight; i += viewportHeight) {
                            window.scrollTo(0, i);
                        }
                    }
                """)
                await page.wait_for_timeout(2000)  # Wait for any dynamic content
                
                html = await page.content()
                return html

            except Exception as e:
                print(f"Error during page load: {str(e)}")
                # Try to get whatever content we have
                try:
                    return await page.content()
                except:
                    return ""
            finally:
                await browser.close()

    async def _handle_route(self, route):
        try:
            await route.continue_()
        except Exception as e:
            print(f"Route handling error: {str(e)}")
            try:
                await route.abort()
            except:
                pass
