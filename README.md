# Content Creation Automation

This project automates the process of generating a video from a tweet and a background image. It uses Playwright to interact with [Tweetpik](https://tweethunter.io/tweetpik), downloads a styled tweet image, and converts it into a vertical video suitable for social media reels.

## Features

- Automates Tweetpik to generate tweet images with custom templates and settings.
- Supports uploading a custom background image.
- Converts the downloaded image into a 1080x1920 vertical video using MoviePy.
- CLI prompts for tweet URL and background image path.

## Requirements

- Python 3.8+
- [Playwright](https://playwright.dev/python/)
- [MoviePy](https://zulko.github.io/moviepy/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [Xvfb](https://en.wikipedia.org/wiki/Xvfb) (for headless environments, e.g., servers or Docker)

## Installation

1. **Clone the repository:**
  ```bash
  git clone https://github.com/noiz-x/content-creation.git
  cd content-creation
  ```

2. **Install dependencies:**
  ```bash
  pip install -r requirements.txt
  playwright install
  ```

3. **Set up environment variables:**

  Create a `.env` file in the project root:
  ```
  DOWNLOAD_DIR=/absolute/path/to/your/download/directory
  ```

## Usage

**Recommended command for running (especially on headless servers):**
```bash
xvfb-run --auto-servernum --server-args="-screen 0 1920x1080x24" python3 main.py
```

**Steps:**
1. Run the above command.
2. Enter the tweet URL when prompted.
3. Enter the path to your background image when prompted.
4. The script will download the styled tweet image and convert it into a vertical video in your `DOWNLOAD_DIR`.

## Notes

- The script launches a visible browser window by default (`headless=False`). For true headless operation, you may set `headless=True` in the code.
- Ensure your `DOWNLOAD_DIR` exists and is writable.
- The output video will be named after the downloaded image, with `_reel.mp4` appended.

## Troubleshooting

- If you encounter issues with Playwright or browser automation, ensure all Playwright browsers are installed:
  ```bash
  playwright install
  ```
- For display errors on servers, ensure `xvfb` is installed and use the provided `xvfb-run` command.

## License

[MIT License](LICENSE)

## Acknowledgements

- [Playwright](https://playwright.dev/python/)
- [MoviePy](https://zulko.github.io/moviepy/)
- [Tweetpik](https://tweethunter.io/tweetpik)
- [python-dotenv](https://pypi.org/project/python-dotenv/)