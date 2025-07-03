# scraper.py

import asyncio
from datetime import datetime, timedelta, timezone
from playwright.async_api import async_playwright

# Input usernames here
usernames = [
    "dtop1percentmen",
    "TheRich_Gospel",
    "YourPrimePath",
    "FitAndFortune",
    "DearS_o_n",
    "Dearme2_",
]

# Scrape settings
DAYS_LIMIT = 90
MAX_TWEETS_PER_USER = 50  # Adjust if needed

def is_recent(tweet_datetime: datetime) -> bool:
    return tweet_datetime >= datetime.now(timezone.utc) - timedelta(days=DAYS_LIMIT)

async def scrape_user_tweets(playwright, username: str):
    print(f"[+] Scraping @{username}...")
    url = f"https://x.com/{username}"
    tweet_links = set()

    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto(url)

    try:
        await page.wait_for_selector("article", timeout=10000)
    except:
        print(f"[-] Failed to load tweets for @{username}")
        await browser.close()
        return []

    last_height = 0
    while len(tweet_links) < MAX_TWEETS_PER_USER:
        articles = await page.query_selector_all("article")
        for article in articles:
            try:
                # Get timestamp
                time_elem = await article.query_selector("time")
                if not time_elem:
                    continue
                datetime_str = await time_elem.get_attribute("datetime")
                tweet_date = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))

                if not is_recent(tweet_date):
                    continue  # Skip old tweets

                # Get link
                link_elem = await article.query_selector("a[role='link'][href*='/status/']")
                if not link_elem:
                    continue
                href = await link_elem.get_attribute("href")
                full_link = f"https://x.com{href}"
                tweet_links.add(full_link)

            except Exception:
                continue

        await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
        await page.wait_for_timeout(2000)

        new_height = await page.evaluate("document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    await browser.close()
    return list(tweet_links)

async def main():
    all_links = []
    async with async_playwright() as playwright:
        for username in usernames:
            links = await scrape_user_tweets(playwright, username)
            all_links.extend(links)
            print(f"[✓] Scraped {len(links)} tweets from @{username}")

    filename = "tweets_all_users.txt"
    with open(filename, "w", encoding="utf-8") as f:
        for link in all_links:
            f.write(link + "\n")
    print(f"[✓] Saved {len(all_links)} tweets to {filename}")

if __name__ == "__main__":
    asyncio.run(main())
