"""
Test Tools
Unit tests for external API integrations (Tavily, ArXiv, Web scrapers).
"""

import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Ensure root folder is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.web_search import TavilySearchTool
from tools.arxiv_fetch import ArxivFetchTool
from tools.web_fetch import WebFetchTool


class TestTools(unittest.TestCase):
    @patch("tools.web_search.TavilyClient")
    def test_web_search(self, mock_tavily_client):
        mock_instance = MagicMock()
        mock_tavily_client.return_value = mock_instance
        mock_instance.search.return_value = {
            "results": [
                {
                    "title": "Result 1",
                    "url": "https://example.com/1",
                    "content": "Snippet 1",
                    "score": 0.95,
                }
            ]
        }

        tool = TavilySearchTool(api_key="fake-key")
        results = tool.search("superconductivity")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Result 1")
        self.assertEqual(results[0]["url"], "https://example.com/1")
        self.assertEqual(results[0]["content"], "Snippet 1")
        mock_instance.search.assert_called_once_with(
            query="superconductivity", max_results=5, search_depth="advanced"
        )

    @patch("tools.arxiv_fetch.requests.get")
    @patch("tools.arxiv_fetch.fitz.open")
    def test_arxiv_fetch(self, mock_fitz_open, mock_requests_get):
        # 1. Test search_papers
        mock_xml_response = MagicMock()
        mock_xml_response.status_code = 200
        mock_xml_response.content = b"""<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
          <entry>
            <id>http://arxiv.org/abs/2307.12008v1</id>
            <title>Room Temperature Superconductors</title>
            <summary>We found superconductivity at room temperature.</summary>
            <link title="pdf" href="http://arxiv.org/pdf/2307.12008v1" rel="related" type="application/pdf"/>
          </entry>
        </feed>
        """
        mock_requests_get.return_value = mock_xml_response

        tool = ArxivFetchTool()
        papers = tool.search_papers("superconductors")

        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0]["title"], "Room Temperature Superconductors")
        self.assertEqual(papers[0]["pdf_url"], "https://arxiv.org/pdf/2307.12008v1")

        # 2. Test parse_pdf
        mock_pdf_response = MagicMock()
        mock_pdf_response.status_code = 200
        mock_pdf_response.content = b"fake-pdf-content"
        mock_requests_get.return_value = mock_pdf_response

        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "This is paper text."
        mock_doc.__iter__.return_value = [mock_page]
        mock_fitz_open.return_value = mock_doc

        text = tool.parse_pdf("https://arxiv.org/pdf/2307.12008v1")
        self.assertIn("This is paper text.", text)
        mock_fitz_open.assert_called_once()
        mock_doc.close.assert_called_once()

    @patch("tools.web_fetch.requests.get")
    @patch("tools.web_fetch.trafilatura.extract")
    def test_web_fetch_standard_success(
        self, mock_trafilatura_extract, mock_requests_get
    ):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Main Article Content</body></html>"
        mock_requests_get.return_value = mock_response
        mock_trafilatura_extract.return_value = "Parsed Main Article Content"

        tool = WebFetchTool()
        content = tool.fetch_url("https://example.com/article")

        self.assertEqual(content, "Parsed Main Article Content")
        self.assertEqual(tool.total_fetches, 1)
        self.assertEqual(tool.empty_fetches, 0)

    @patch("tools.web_fetch.requests.get")
    @patch("tools.web_fetch.trafilatura.extract")
    @patch("tools.web_fetch.sync_playwright")
    def test_web_fetch_playwright_fallback(
        self, mock_sync_playwright, mock_trafilatura_extract, mock_requests_get
    ):
        # Standard fetch fails
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body></body></html>"
        mock_requests_get.return_value = mock_response
        mock_trafilatura_extract.side_effect = [None, "Playwright Rendered Content"]

        # Playwright mock
        mock_playwright = MagicMock()
        mock_sync_playwright.return_value.__enter__.return_value = mock_playwright
        mock_browser = MagicMock()
        mock_playwright.chromium.launch.return_value = mock_browser
        mock_context = MagicMock()
        mock_browser.new_context.return_value = mock_context
        mock_page = MagicMock()
        mock_context.new_page.return_value = mock_page
        mock_page.content.return_value = "<html><body>Rendered HTML</body></html>"

        tool = WebFetchTool()
        content = tool.fetch_url("https://example.com/js-rendered")

        self.assertEqual(content, "Playwright Rendered Content")
        self.assertEqual(tool.total_fetches, 1)
        self.assertEqual(tool.empty_fetches, 0)
        mock_page.goto.assert_called_once_with(
            "https://example.com/js-rendered", wait_until="networkidle", timeout=20000
        )


if __name__ == "__main__":
    unittest.main()
