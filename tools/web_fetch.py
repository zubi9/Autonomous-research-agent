"""
Web Fetch Tool
Scrapes HTML contents from target URLs, cleans elements, and extracts readable text.
"""

import requests
import trafilatura
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


class WebFetchTool:
    def __init__(self):
        self.total_fetches = 0
        self.empty_fetches = 0

    def fetch_url(self, url: str) -> str:
        """Fetches the URL content, cleans up HTML, and returns readable text/markdown.
        Falls back to Playwright if standard requests return empty content, or if the
        failure rate of standard requests is >= 70%.
        """
        self.total_fetches += 1

        # Check if historical failure rate is >= 70% (min 3 attempts to avoid early bias)
        use_playwright_direct = False
        if (
            self.total_fetches >= 3
            and (self.empty_fetches / self.total_fetches) >= 0.70
        ):
            use_playwright_direct = True

        content = ""
        if not use_playwright_direct:
            content = self._fetch_standard(url)

        if not content:
            print(
                f"Standard fetch returned empty for {url}. Falling back to Playwright..."
            )
            content = self._fetch_playwright(url)
            if not content:
                self.empty_fetches += 1

        return content

    def _fetch_standard(self, url: str) -> str:
        """Standard HTTP request + Trafilatura parsing."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                return ""

            # Use trafilatura to extract readable main text
            downloaded = response.text
            extracted = trafilatura.extract(
                downloaded, include_links=True, include_images=False
            )
            if extracted:
                return extracted

            # Fallback to BeautifulSoup if trafilatura fails to extract
            soup = BeautifulSoup(downloaded, "html.parser")
            for element in soup(["script", "style", "nav", "footer", "header"]):
                element.decompose()
            return soup.get_text(separator="\n").strip()
        except Exception as e:
            print(f"Error during standard fetch of {url}: {e}")
            return ""

    def _fetch_playwright(self, url: str) -> str:
        """Headless Playwright browser extraction as a robust fallback."""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                page = context.new_page()
                page.goto(url, wait_until="networkidle", timeout=20000)
                html = page.content()
                browser.close()

                # Clean up rendered HTML
                extracted = trafilatura.extract(
                    html, include_links=True, include_images=False
                )
                if extracted:
                    return extracted

                soup = BeautifulSoup(html, "html.parser")
                for element in soup(["script", "style", "nav", "footer", "header"]):
                    element.decompose()
                return soup.get_text(separator="\n").strip()
        except Exception as e:
            print(f"Error during Playwright fetch of {url}: {e}")
            return ""
