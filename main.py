import re
from playwright.sync_api import Playwright, sync_playwright, expect
from scraper import fetch_html_playwright, save_raw_data, html_to_markdown_with_readability
from datetime import datetime

def main():
    url = "https://meetings.asco.org/abstracts-presentations/232037"
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    raw_html =  fetch_html_playwright(url)
    markdown = html_to_markdown_with_readability(raw_html)
    save_raw_data(markdown, timestamp)

# Running the async function
if __name__ == "__main__":
     main()