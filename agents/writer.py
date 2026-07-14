import os
from langchain_openai import ChatOpenAI


class WriterAgent:
    def __init__(self):
        openai_api_key = os.getenv("OPENAI_API_KEY")
        # Project plan specifies gpt-4o for writer and gpt-4o-mini for speed/cost elsewhere
        self.llm = None
        if openai_api_key:
            self.llm = ChatOpenAI(
                model="gpt-4o", temperature=0.3, api_key=openai_api_key
            )

    def synthesize_report(
        self, query: str, summaries: list[str], citations: list[dict]
    ) -> str:
        """Synthesizes summaries and citation information into a comprehensive report."""
        print("Writer Node synthesizing report...")

        # Combine section summaries
        summaries_context = ""
        for idx, summary in enumerate(summaries):
            summaries_context += f"Research Section {idx + 1}:\n{summary}\n\n"

        # Deduplicate citations to build references
        deduped_citations = []
        seen_urls = set()
        for cit in citations:
            url = cit.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                deduped_citations.append(cit)

        citations_context = "Citations Context:\n"
        for idx, cit in enumerate(deduped_citations):
            citations_context += f"[{idx + 1}] {cit.get('title', 'Unknown Source')} - URL: {cit.get('url')}\n"

        system_msg = (
            "You are an expert report writer and senior research director. Your role is to write a comprehensive, "
            "authoritative research report based on a set of research section summaries and source citations.\n"
            "Format the report in elegant markdown. It must contain:\n"
            "1. A clear Title\n"
            "2. Executive Summary\n"
            "3. Detailed Findings (organized with sections, headers, and bullet points)\n"
            "4. A 'References' or 'Sources' appendix listing every unique citation URL with clickable markdown links.\n"
            "Ensure the body of your report uses proper inline numbering links like [1] that correspond to the items "
            "in your References list. Synthesize sections logically to flow seamlessly without duplicating introductory text."
        )

        user_msg = (
            f"Original Query: {query}\n\n"
            f"Summaries Collected:\n{summaries_context}\n"
            f"Sources Available:\n{citations_context}"
        )

        if self.llm is None:
            return self._fallback_report(query, summaries, deduped_citations)

        try:
            response = self.llm.invoke([("system", system_msg), ("user", user_msg)])
            return response.content
        except Exception as e:
            print(f"Error in WriterAgent synthesis: {e}")
            return self._fallback_report(query, summaries, deduped_citations)

    def _fallback_report(
        self, query: str, summaries: list[str], citations: list[dict]
    ) -> str:
        reference_lines = []
        for idx, citation in enumerate(citations, start=1):
            title = citation.get("title", "Untitled Source")
            url = citation.get("url", "")
            reference_lines.append(f"[{idx}] {title} - {url}")

        references = (
            "\n".join(reference_lines)
            if reference_lines
            else "No sources were collected."
        )
        summary_points = (
            "\n".join(f"- {summary}" for summary in summaries)
            if summaries
            else "- No summary content was provided."
        )

        return (
            f"# Research Report: {query}\n\n"
            f"## Executive Summary\n"
            f"This report was synthesized locally because no OpenAI API key was configured.\n\n"
            f"## Detailed Findings\n{summary_points}\n\n"
            f"## References\n{references}"
        )
