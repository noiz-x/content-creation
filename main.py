# main.py

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

async def main():
    tweet_url = "https://x.com/UnscriptedFooty/status/1937068032259424331"
    image_path = "/home/atsuomi/Pictures/samurai_champloo.jpg"
    download_dir = Path("/home/atsuomi/Downloads")  # Adjust this to where you want to save

    if not Path(image_path).is_file():
        print(f"❌ Image not found at path: {image_path}")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(accept_downloads=True)
        page = await context.new_page()

        print("🌐 Navigating to Tweetpik...")
        await page.goto("https://tweethunter.io/tweetpik", timeout=60000)

        print("⌨️ Filling tweet URL...")
        await page.fill('input[name="url"]', tweet_url)
        await page.click('button[type="submit"]')

        print("🔍 Selecting tweet...")
        await page.wait_for_selector('section#loadedTweets button', timeout=15000)
        tweets = await page.query_selector_all('section#loadedTweets button')
        if tweets:
            await tweets[0].click()
        else:
            print("❌ No tweets found.")
            return

        print("🎨 Choosing template...")
        await page.wait_for_selector('div.css-fnxeue > div', timeout=15000)
        templates = await page.query_selector_all('div.css-fnxeue > div')
        if len(templates) >= 2:
            await templates[1].click()
        else:
            print("❌ Less than 2 templates found.")
            return

        print("📁 Uploading background image...")
        await page.set_input_files('input[type="file"]#backgroundImage', image_path)

        print("⬇️ Downloading image...")
        # Set up listener for download BEFORE clicking download button
        async with page.expect_download() as download_info:
            await page.click('button.chakra-button.css-8oiimi')  # "Download" button

        download = await download_info.value

        # Save to target directory with auto-generated filename
        download_path = download.suggested_filename
        final_path = download_dir / download_path
        await download.save_as(final_path)

        print(f"✅ Download complete: {final_path}")

        await browser.close()

asyncio.run(main())
