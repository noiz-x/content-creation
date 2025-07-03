# main.py

import asyncio
import os
import random
from pathlib import Path
from dotenv import load_dotenv
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip
from playwright.async_api import async_playwright


def create_video_from_image(image_path: Path, output_path: Path, duration=1.5):
    print("🎬 Converting image to video...")

    # Ensure minimum 10 seconds
    duration = max(duration, 10)

    # Create image clip
    clip = ImageClip(str(image_path)).set_duration(duration)

    # Resize to vertical 1080x1920
    clip = clip.resize(height=1920)
    if clip.w < 1080:
        margin = (1080 - clip.w) // 2
        clip = clip.margin(left=margin, right=margin, color=(0, 0, 0))
    elif clip.w > 1080:
        clip = clip.resize(width=1080)

    clip = clip.set_fps(24)

    # Load random audio from 'sounds' directory
    sounds_dir = Path("sounds")
    audio_files = list(sounds_dir.glob("*.mp3")) + list(sounds_dir.glob("*.wav")) + list(sounds_dir.glob("*.ogg"))
    if not audio_files:
        raise FileNotFoundError("❌ No audio files found in 'sounds' folder.")
    selected_audio = random.choice(audio_files)
    audio_clip = AudioFileClip(str(selected_audio)).subclip(0, duration)

    # Combine video and audio
    final_video = clip.set_audio(audio_clip)

    # Write final video
    final_video.write_videofile(str(output_path), codec='libx264', audio_codec='aac', fps=24)
    print(f"✅ Video saved to {output_path}")


def get_all_tweets():
    with open("tweets_all_users.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def get_random_background():
    panel_dir = Path("manga_panels")
    if not panel_dir.exists():
        raise FileNotFoundError("❌ 'manga_panels' folder not found.")
    images = list(panel_dir.glob("*.jpg")) + list(panel_dir.glob("*.jpeg")) + list(panel_dir.glob("*.png"))
    if not images:
        raise FileNotFoundError("❌ No images found in 'manga_panels'.")
    return random.choice(images)


async def process_tweet(page, tweet_url, image_path, download_dir):
    print(f"🌐 Navigating to Tweetpik for {tweet_url}...")
    await page.goto("https://tweethunter.io/tweetpik", timeout=60000)

    print("⌨️ Filling tweet URL...")
    await page.fill('input[name="url"]', tweet_url)
    await page.click('button[type="submit"]')

    print("🔍 Selecting tweet...")
    try:
        await page.wait_for_selector('section#loadedTweets button', timeout=15000)
        tweets = await page.query_selector_all('section#loadedTweets button')
        if not tweets:
            print("❌ No tweets found.")
            return
        await tweets[0].click()
    except Exception as e:
        print("❌ Error selecting tweet:", e)
        return

    print("🎨 Choosing template...")
    try:
        await page.wait_for_selector('div.css-fnxeue > div', timeout=15000)
        templates = await page.query_selector_all('div.css-fnxeue > div')
        if len(templates) < 2:
            print("❌ Less than 2 templates found.")
            return
        await templates[1].click()
    except Exception as e:
        print("❌ Template selection error:", e)
        return

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

    print("📁 Uploading background image:", image_path)
    await page.set_input_files('input[type="file"]#backgroundImage', str(image_path))

    print("⬇️ Downloading image...")
    try:
        async with page.expect_download() as download_info:
            await page.click('button.chakra-button.css-8oiimi')
        download = await download_info.value
        final_path = download_dir / download.suggested_filename
        await download.save_as(final_path)
        print(f"✅ Download complete: {final_path}")

        # Convert image to video with audio
        video_output = download_dir / (final_path.stem + "_reel.mp4")
        create_video_from_image(final_path, video_output, duration=1.5)
    except Exception as e:
        print("❌ Download failed:", e)


async def main():
    load_dotenv()
    download_dir = Path(os.getenv("DOWNLOAD_DIR", "downloads"))
    download_dir.mkdir(exist_ok=True)

    tweet_urls = get_all_tweets()
    if not tweet_urls:
        print("❌ No tweets found in tweets_all_users.txt")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(accept_downloads=True)
        page = await context.new_page()

        for tweet_url in tweet_urls:
            image_path = get_random_background()
            print(f"\n🧠 Processing tweet: {tweet_url}")
            try:
                await process_tweet(page, tweet_url, image_path, download_dir)
            except Exception as e:
                print(f"❌ Error processing {tweet_url}: {e}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
