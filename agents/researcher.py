import os
from langchain_openai import ChatOpenAI
from tools.web_search import TavilySearchTool
from tools.arxiv_fetch import ArxivFetchTool
from tools.web_fetch import WebFetchTool


class ResearcherAgent:
    def __init__(self):
        openai_api_key = os.getenv("OPENAI_API_KEY")
        self.llm = None
        if openai_api_key:
            self.llm = ChatOpenAI(
                model="gpt-4o-mini", temperature=0.2, api_key=openai_api_key
            )
        self.web_search = TavilySearchTool()
        self.arxiv_fetch = ArxivFetchTool()
        self.web_fetch = WebFetchTool()

    def execute_task(self, sub_query: str, source: str) -> dict:
        """Runs search queries, crawls content, and outputs a synthesized summary with citations."""
        print(f"Researcher Node executing: '{sub_query}' via source '{source}'")
        documents = []
        citations = []

        try:
            if source == "arxiv":
                papers = self.arxiv_fetch.search_papers(sub_query, limit=3)
                for paper in papers:
                    pdf_url = paper.get("pdf_url", "")
                    title = paper.get("title", "")
                    print(f"Downloading and parsing PDF: {title} ({pdf_url})")
                    pdf_text = self.arxiv_fetch.parse_pdf(pdf_url)
                    snippet = pdf_text[:6000] if pdf_text else paper.get("summary", "")

                    documents.append(
                        {
                            "title": title,
                            "text": snippet,
                            "url": pdf_url,
                            "source": "arxiv",
                        }
                    )
                    citations.append(
                        {"title": title, "url": pdf_url, "source": "arxiv"}
                    )
            else:  # web search
                search_results = self.web_search.search(sub_query, max_results=3)
                for res in search_results:
                    url = res.get("url", "")
                    title = res.get("title", "")
                    print(f"Scraping web page: {title} ({url})")
                    web_text = self.web_fetch.fetch_url(url)
                    snippet = web_text[:5000] if web_text else res.get("content", "")

                    documents.append(
                        {"title": title, "text": snippet, "url": url, "source": "web"}
                    )
                    citations.append({"title": title, "url": url, "source": "web"})
        except Exception as e:
            print(f"Error during search/fetch: {e}")

        if not documents:
            return {
                "summary": f"Failed to gather documents for query: {sub_query}",
                "citations": [],
            }

        # Compile context for the LLM
        context_str = ""
        for idx, doc in enumerate(documents):
            context_str += f"Source [{idx + 1}]: {doc['title']} (URL: {doc['url']})\nContent Snippet:\n{doc['text']}\n\n"

        if self.llm is None:
            summary_text = self._fallback_summary(sub_query, documents)
        else:
            system_msg = (
                "You are a meticulous research analyst. Summarize the provided document context specifically in relation "
                "to the research question. Be factual, concise, and structured. Use inline citation references like [Source 1], "
                "matching the source index numbers provided in the context."
            )
            user_msg = (
                f"Research Question: {sub_query}\n\nDocument Context:\n{context_str}"
            )

            try:
                summary_response = self.llm.invoke(
                    [("system", system_msg), ("user", user_msg)]
                )
                summary_text = summary_response.content
            except Exception as e:
                print(f"Error generating summary: {e}")
                summary_text = self._fallback_summary(sub_query, documents)

        return {"summary": summary_text, "citations": citations, "documents": documents}

    def _fallback_summary(self, sub_query: str, documents: list[dict]) -> str:
        top_documents = documents[:3]
        bullet_points = []
        for idx, doc in enumerate(top_documents, start=1):
            title = doc.get("title", f"Document {idx}")
            snippet = (doc.get("text") or "").strip()
            bullet_points.append(f"- {title}: {snippet[:220]}")

        joined = (
            "\n".join(bullet_points)
            if bullet_points
            else "No supporting documents were collected."
        )
        return (
            f"Fallback summary for '{sub_query}':\n"
            f"The available evidence suggests the topic is covered by the following sources:\n{joined}"
        )
