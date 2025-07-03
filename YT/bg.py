# bg.py

import httpx
import random
import os
from pathlib import Path
from tqdm import tqdm

BASE_URL = "https://api.mangadex.org"
SAVE_DIR = Path("manga_panels")
SAVE_DIR.mkdir(exist_ok=True)

HEADERS = {
    "User-Agent": "RandomMangaPanelFetcher/1.0"
}

def get_random_manga_id():
    params = {
        "limit": 20,
        "availableTranslatedLanguage[]": "en",
        "order[followedCount]": "desc"
    }
    try:
        res = httpx.get(f"{BASE_URL}/manga", params=params, headers=HEADERS, timeout=10)
        manga_list = res.json()["data"]
        if not manga_list:
            return None
        return random.choice(manga_list)["id"]
    except Exception:
        return None

def get_random_chapter_id(manga_id):
    params = {
        "limit": 20,
        "translatedLanguage[]": "en",
        "order[chapter]": "asc"
    }
    try:
        res = httpx.get(f"{BASE_URL}/manga/{manga_id}/feed", params=params, headers=HEADERS, timeout=10)
        chapter_list = res.json()["data"]
        if not chapter_list:
            return None
        return random.choice(chapter_list)["id"]
    except Exception:
        return None

def get_random_page_url(chapter_id):
    try:
        res = httpx.get(f"{BASE_URL}/at-home/server/{chapter_id}", headers=HEADERS, timeout=10)
        data = res.json()
        if not data or "chapter" not in data:
            return None
        base_url = data["baseUrl"]
        hash_val = data["chapter"]["hash"]
        pages = data["chapter"]["data"]
        if not pages:
            return None
        page = random.choice(pages)
        return f"{base_url}/data/{hash_val}/{page}"
    except Exception:
        return None

def download_image(url: str, index: int):
    try:
        img_data = httpx.get(url, headers=HEADERS, timeout=10).content
        ext = url.split(".")[-1].split("?")[0]
        filename = SAVE_DIR / f"panel_{index:03d}.{ext}"
        with open(filename, "wb") as f:
            f.write(img_data)
        return True
    except Exception:
        return False

def get_random_panel_url():
    manga_id = get_random_manga_id()
    if not manga_id:
        return None
    chapter_id = get_random_chapter_id(manga_id)
    if not chapter_id:
        return None
    return get_random_page_url(chapter_id)

def main():
    total = 20
    downloaded = 0
    attempts = 0
    urls = []

    with tqdm(total=total, desc="Downloading panels") as pbar:
        while downloaded < total and attempts < total * 10:
            url = get_random_panel_url()
            attempts += 1
            if url and url not in urls:
                success = download_image(url, downloaded + 1)
                if success:
                    urls.append(url)
                    downloaded += 1
                    pbar.update(1)

    # Save URLs
    with open("manga_panel_links.txt", "w", encoding="utf-8") as f:
        for link in urls:
            f.write(link + "\n")

    print(f"\n✅ Downloaded {downloaded} manga panels to: {SAVE_DIR}")
    print("🔗 Links saved to: manga_panel_links.txt")

if __name__ == "__main__":
    main()
