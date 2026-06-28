"""
ArXiv Fetch Tool
Queries ArXiv API, downloads relevant research papers, and parses PDF content.
"""

import urllib.parse
import xml.etree.ElementTree as ET
import requests
import fitz  # PyMuPDF
import io


class ArxivFetchTool:
    def __init__(self):
        pass

    def search_papers(self, query: str, limit: int = 5) -> list[dict]:
        """Queries ArXiv for relevant papers and returns metadata."""
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"http://export.arxiv.org/api/query?search_query=all:{encoded_query}&max_results={limit}"
            response = requests.get(url, timeout=15)
            if response.status_code != 200:
                print(f"ArXiv query failed with status code: {response.status_code}")
                return []

            root = ET.fromstring(response.content)
            # ArXiv XML uses the Atom namespace
            ns = {"atom": "http://www.w3.org/2005/Atom"}

            papers = []
            for entry in root.findall("atom:entry", ns):
                title = entry.find("atom:title", ns)
                summary = entry.find("atom:summary", ns)
                id_url = entry.find("atom:id", ns)

                # Extract pdf link
                pdf_url = ""
                for link in entry.findall("atom:link", ns):
                    if (
                        link.attrib.get("title") == "pdf"
                        or link.attrib.get("type") == "application/pdf"
                    ):
                        pdf_url = link.attrib.get("href", "")
                        if pdf_url.startswith("http://"):
                            pdf_url = pdf_url.replace("http://", "https://")
                        break

                if not pdf_url and id_url is not None:
                    raw_id = id_url.text.strip().split("/abs/")[-1]
                    pdf_url = f"https://arxiv.org/pdf/{raw_id}"

                papers.append(
                    {
                        "title": title.text.strip().replace("\n", " ")
                        if title is not None
                        else "No Title",
                        "summary": summary.text.strip()
                        if summary is not None
                        else "No Abstract",
                        "id": id_url.text.strip() if id_url is not None else "",
                        "pdf_url": pdf_url,
                    }
                )
            return papers
        except Exception as e:
            print(f"Error querying ArXiv: {e}")
            return []

    def parse_pdf(self, pdf_url: str) -> str:
        """Downloads and extracts text from a PDF paper using PyMuPDF."""
        if not pdf_url:
            return ""
        try:
            response = requests.get(pdf_url, timeout=30)
            if response.status_code != 200:
                print(
                    f"Failed to download PDF from {pdf_url}: HTTP {response.status_code}"
                )
                return ""

            doc = fitz.open(stream=io.BytesIO(response.content), filetype="pdf")
            text = []
            for page in doc:
                text.append(page.get_text())
            doc.close()
            return "\n".join(text)
        except Exception as e:
            print(f"Error downloading or parsing PDF from {pdf_url}: {e}")
            return ""
