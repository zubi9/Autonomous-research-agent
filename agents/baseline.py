import os
import sys
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.web_search import TavilySearchTool
from tools.arxiv_fetch import ArxivFetchTool
from tools.web_fetch import WebFetchTool

# Load local environment variables
load_dotenv()

# Initialize tool instances
web_search = TavilySearchTool()
arxiv_fetch = ArxivFetchTool()
web_fetch = WebFetchTool()


@tool
def search_tavily(query: str, max_results: int = 5) -> list[dict]:
    """Execute a web search query using Tavily to find web pages, titles, URLs, and snippets."""
    return web_search.search(query, max_results)


@tool
def search_arxiv(query: str, limit: int = 5) -> list[dict]:
    """Search academic articles on ArXiv and return metadata, abstracts, and PDF URLs."""
    return arxiv_fetch.search_papers(query, limit)


@tool
def fetch_web_page(url: str) -> str:
    """Fetch the full clean text of a web page URL. Supports standard parsing and falls back to headless browser rendering."""
    return web_fetch.fetch_url(url)


@tool
def parse_arxiv_pdf(pdf_url: str) -> str:
    """Download and extract the full text of an academic paper PDF from ArXiv using PyMuPDF."""
    return arxiv_fetch.parse_pdf(pdf_url)


tools = [search_tavily, search_arxiv, fetch_web_page, parse_arxiv_pdf]

# System prompt outlining the research task
system_prompt = (
    "You are an expert autonomous research agent. Your task is to investigate the user's research query end-to-end.\n"
    "Use the search tools to find relevant information, fetch the most relevant web pages or academic PDF contents to read them, and synthesize your findings into a comprehensive, high-quality, structured markdown report with citations.\n"
    "Ensure you query both web and academic sources where relevant, read the text of the source materials, and include direct URLs to the sources in your final output."
)

# Initialize LLM and Agent Executor using LangGraph
openai_key = os.getenv("OPENAI_API_KEY") or "mock-key-for-import-validation"
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2, api_key=openai_key)
agent_executor = create_agent(llm, tools=tools, system_prompt=system_prompt)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python baseline.py '<research_query>'")
        sys.exit(1)

    query = sys.argv[1]
    print(f"Starting research on query: {query}")

    try:
        # Run using LangGraph's standard messages format
        result = agent_executor.invoke({"messages": [("user", query)]})
        # The final answer is the content of the last message in the graph's state
        output_report = result["messages"][-1].content

        # Display the report in terminal
        print("\n" + "=" * 40 + " RESEARCH REPORT " + "=" * 40 + "\n")
        print(output_report)
        print("\n" + "=" * 97 + "\n")

        # Save to markdown file
        output_filename = "research_report.md"
        with open(output_filename, "w") as f:
            f.write(output_report)
        print(f"Saved final report to {output_filename}")
    except Exception as e:
        print(f"Error executing agent: {e}")
