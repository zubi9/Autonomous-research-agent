"""Real-data smoke tests for the external tool modules.

These tests call the live ArXiv, web-fetch, and Tavily integrations so you can
verify that each module works against real inputs rather than mocked responses.
"""

from __future__ import annotations

import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.arxiv_fetch import ArxivFetchTool
from tools.web_fetch import WebFetchTool
from tools.web_search import TavilySearchTool


class ToolSmokeTests(unittest.TestCase):
    def test_arxiv_search_and_pdf(self) -> None:
        tool = ArxivFetchTool()
        papers = tool.search_papers("room temperature superconductivity", limit=2)

        self.assertTrue(papers, "ArXiv returned no papers for the sample query")

        first_paper = papers[0]
        text = tool.parse_pdf(first_paper["pdf_url"])

        self.assertTrue(first_paper["title"], "The first paper is missing a title")
        self.assertTrue(text.strip(), "The PDF text extraction returned no content")

    def test_web_fetch_real_page(self) -> None:
        tool = WebFetchTool()
        content = tool.fetch_url("https://www.python.org/")

        self.assertTrue(content.strip(), "The web fetch returned no readable content")
        self.assertIn(
            "Python", content, "The fetched page did not contain the expected content"
        )

    def test_tavily_search_real_query(self) -> None:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            self.skipTest("TAVILY_API_KEY is not set; skipping live Tavily search")

        tool = TavilySearchTool(api_key=api_key)
        results = tool.search(
            "latest developments in room temperature superconductivity", max_results=3
        )

        self.assertTrue(results, "Tavily returned no results for the sample query")
        self.assertTrue(results[0]["url"], "The first Tavily result is missing a URL")


if __name__ == "__main__":
    unittest.main(verbosity=2)
