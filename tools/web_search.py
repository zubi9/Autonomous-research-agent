"""
Web Search Tool
Tavily API wrapper for executing web searches.
"""

import os

from tavily import TavilyClient


class TavilySearchTool:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        self.client = TavilyClient(api_key=self.api_key) if self.api_key else None

    def search(self, query: str, max_results: int = 5) -> list[dict]:
        """Executes a web search query and returns structured results."""
        if not self.client:
            raise ValueError(
                "TAVILY_API_KEY must be set in the environment or passed to TavilySearchTool."
            )
        try:
            response = self.client.search(
                query=query, max_results=max_results, search_depth="advanced"
            )
            results = []
            for result in response.get("results", []):
                results.append(
                    {
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "content": result.get("content", ""),
                        "score": result.get("score", 0.0),
                    }
                )
            return results
        except Exception as e:
            # Return empty list or propagate with error handling
            print(f"Error during Tavily Search: {e}")
            return []
