# main.py

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import os
from moviepy.editor import ImageClip

def create_video_from_image(image_path: Path, output_path: Path, duration=1.5):
    print("🎬 Converting image to video...")
    clip = ImageClip(str(image_path)).set_duration(duration)

    # Set video resolution to vertical (1080x1920)
    clip = clip.resize(height=1920)
    if clip.w < 1080:
        clip = clip.margin(left=(1080 - clip.w) // 2, right=(1080 - clip.w) // 2, color=(0, 0, 0))
    elif clip.w > 1080:
        clip = clip.resize(width=1080)

    clip = clip.set_fps(24)
    clip.write_videofile(str(output_path), codec='libx264', audio=False, fps=24)
    print(f"✅ Video saved to {output_path}")

async def main():
    tweet_url = input("Enter the tweet URL: ")
    image_path = input("Enter the image path: ")
    load_dotenv()
    download_dir = Path(os.getenv("DOWNLOAD_DIR"))

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
        if not tweets:
            print("❌ No tweets found.")
            return
        await tweets[0].click()

        print("🎨 Choosing template...")
        await page.wait_for_selector('div.css-fnxeue > div', timeout=15000)
        templates = await page.query_selector_all('div.css-fnxeue > div')
        if len(templates) < 2:
            print("❌ Less than 2 templates found.")
            return
        await templates[1].click()

        # ================= SETTINGS START =================
        print("⚙️ Setting dimensions to auto height...")
        await page.select_option('select#dimension', 'instagramFeedVertical')

        print("☑️ Enabling metrics, media, and time...")

        async def enable_checkbox(label_id: str):
            checkbox_wrapper = await page.query_selector(f'label[for="{label_id}"] + label span.chakra-checkbox__control')
            if checkbox_wrapper:
                is_checked = await checkbox_wrapper.get_attribute("data-checked")
                if not is_checked:
                    await checkbox_wrapper.click()
                    await asyncio.sleep(0.2)

        await enable_checkbox("displayMetrics")
        await enable_checkbox("displayEmbeds")
        await enable_checkbox("displayTime")
        # ================= SETTINGS END ===================

        print("📁 Uploading background image...")
        await page.set_input_files('input[type="file"]#backgroundImage', image_path)

        print("⬇️ Downloading image...")
        async with page.expect_download() as download_info:
            await page.click('button.chakra-button.css-8oiimi')  # "Download" button

        download = await download_info.value
        final_path = download_dir / download.suggested_filename
        await download.save_as(final_path)
        print(f"✅ Download complete: {final_path}")

        # Convert image to video
        video_output = download_dir / (final_path.stem + "_reel.mp4")
        create_video_from_image(final_path, video_output, duration=1.5)

        await browser.close()

asyncio.run(main())
