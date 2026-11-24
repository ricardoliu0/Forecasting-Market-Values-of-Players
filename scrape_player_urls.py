"""
SoFIFA Player URL Scraper.

Collect player profile URLs from the paginated player list.
"""

import asyncio
import csv
from pathlib import Path

from playwright.async_api import async_playwright

BASE = Path(__file__).resolve().parent


class PlayerURLScraper:
    def __init__(self, base_url="https://sofifa.com/players?col=oa&sort=desc"):
        self.base_url = base_url
        self.all_player_urls = []
        self.offset = 0
        self.page_size = 60
        self.pages_scraped = 0
        self.completed = False

    async def scrape_all_player_urls(self):
        """Collect player URLs and save progress after each page."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                    "--disable-setuid-sandbox"
                ]
            )

            try:
                context = await browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    ),
                    viewport={"width": 1920, "height": 1080},
                    locale="en-US",
                    timezone_id="America/New_York",
                    extra_http_headers={
                        "Accept-Language": "en-US,en;q=0.9",
                        "Accept": (
                            "text/html,application/xhtml+xml,"
                            "application/xml;q=0.9,*/*;q=0.8"
                        ),
                        "Sec-Fetch-Dest": "document",
                        "Sec-Fetch-Mode": "navigate",
                        "Sec-Fetch-Site": "none"
                    }
                )

                page = await context.new_page()

                # Block nonessential resources to reduce page load time.
                async def handle_route(route):
                    blocked_types = {"image", "stylesheet", "font", "media"}
                    if route.request.resource_type in blocked_types:
                        await route.abort()
                    else:
                        await route.continue_()

                await page.route("**/*", handle_route)

                page_num = 1
                has_next = True

                while has_next:
                    url = (
                        f"{self.base_url}&offset={self.offset}"
                        if self.offset > 0
                        else self.base_url
                    )

                    max_attempts = 3
                    success = False

                    for attempt in range(1, max_attempts + 1):
                        try:
                            if attempt > 1:
                                print(
                                    f"Retrying page {page_num}: "
                                    f"attempt {attempt}/{max_attempts} "
                                    "after a 10-second pause."
                                )
                                await asyncio.sleep(10)

                            print(f"\n[Page {page_num}] Scraping: {url}")

                            await page.goto(
                                url,
                                wait_until="domcontentloaded",
                                timeout=15000
                            )
                            await page.wait_for_timeout(2000)

                            # Detect verification pages.
                            page_content = await page.content()
                            challenge_markers = [
                                "Checking your browser",
                                "Just a moment",
                                "cf-browser-verification"
                            ]
                            if any(
                                marker in page_content
                                for marker in challenge_markers
                            ):
                                print("Cloudflare challenge detected.")
                                continue

                            # Extract unique profile URLs and pagination status.
                            page_data = await page.evaluate("""
                                () => {
                                    const urls = [];
                                    const links = document.querySelectorAll(
                                        'a[href*="/player/"]'
                                    );

                                    links.forEach(link => {
                                        const href = link.href;
                                        if (
                                            href &&
                                            href.includes('/player/') &&
                                            !href.includes('random') &&
                                            !urls.includes(href)
                                        ) {
                                            urls.push(href);
                                        }
                                    });

                                    const nextButton = [
                                        ...document.querySelectorAll('a.button')
                                    ].find(
                                        a => a.textContent.includes('Next')
                                    );

                                    return {
                                        urls,
                                        hasNext: Boolean(nextButton)
                                    };
                                }
                            """)

                            player_urls = page_data["urls"]
                            if not player_urls:
                                raise RuntimeError(
                                    "No player URLs found on this page."
                                )

                            has_next = page_data["hasNext"]
                            self.all_player_urls.extend(player_urls)
                            self.save_urls_to_csv()
                            self.pages_scraped += 1

                            print(
                                f"Extracted {len(player_urls)} player URLs."
                            )
                            print("Next button exists:", has_next)

                            success = True
                            break

                        except Exception as exc:
                            print(f"Error: {exc}")

                    # Stop pagination after repeated failures.
                    if not success:
                        print(
                            f"Stopped after {max_attempts} unsuccessful "
                            f"attempts on page {page_num}. "
                            "Previously collected URLs have been preserved."
                        )
                        break

                    if has_next:
                        self.offset += self.page_size
                        page_num += 1
                    else:
                        self.completed = True

            finally:
                await browser.close()

        return self.all_player_urls

    def save_urls_to_csv(self, filename="player_urls.csv"):
        """Save unique URLs while preserving their original order."""
        filename = Path(filename)
        if not filename.is_absolute():
            filename = BASE / filename

        unique_urls = list(dict.fromkeys(self.all_player_urls))

        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["player_url"])
            writer.writerows([url] for url in unique_urls)

        print(f"Saved {len(unique_urls)} unique URLs to {filename}")


async def main():
    """Run the URL scraper and report the final status."""
    scraper = PlayerURLScraper()

    print("=" * 60)
    print("SoFIFA Player URL Scraper")
    print("=" * 60)
    print("Collecting player profile URLs from the player list.")
    print("Progress is saved after each successful page.")

    await scraper.scrape_all_player_urls()

    print("\n" + "=" * 60)
    if scraper.completed:
        print("SCRAPING COMPLETED")
    else:
        print("SCRAPING STOPPED BEFORE COMPLETION")
    print("=" * 60)

    print(
        "Total unique player URLs:",
        len(set(scraper.all_player_urls))
    )
    print("Pages successfully scraped:", scraper.pages_scraped)

    if scraper.all_player_urls:
        print("Output file:", BASE / "player_urls.csv")
    else:
        print("No URLs collected. No output file was written.")


if __name__ == "__main__":
    asyncio.run(main())