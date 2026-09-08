import urllib.parse

import requests


class CitationManager:
    def __init__(self):
        pass

    def deduplicate(self, citations: list) -> list:
        """Removes duplicate links and aggregates citations."""
        seen_urls = set()
        deduped = []
        for cit in citations:
            url = cit.get("url", "").strip()
            if url and url not in seen_urls:
                seen_urls.add(url)
                deduped.append(cit)
        return deduped

    def calculate_confidence(self, citation: dict) -> float:
        """Computes confidence metric based on domains, citations, and content checks."""
        url = citation.get("url", "")
        if not url:
            return 0.0

        score = 0.50  # Base fallback score

        # 1. Domain-based scoring
        try:
            parsed_url = urllib.parse.urlparse(url)
            domain = parsed_url.netloc.lower()

            if "arxiv.org" in domain:
                score = 0.95
            elif domain.endswith((".edu", ".gov")):
                score = 0.90
            elif domain.endswith(".org"):
                score = 0.80
            elif domain.endswith((".com", ".net", ".co")):
                score = 0.70
        except ValueError:
            pass

        # 2. Liveliness Check (Head/GET Request with Timeout)
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            # Try HEAD first
            response = requests.head(
                url, headers=headers, timeout=5, allow_redirects=True
            )
            if response.status_code >= 400:
                response = requests.get(url, headers=headers, timeout=5)

            if response.status_code < 400:
                score += 0.05
            else:
                score -= 0.30
        except requests.RequestException:
            score -= 0.20

        return min(max(round(score, 2), 0.0), 1.0)
