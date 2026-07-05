import os
from pydantic import BaseModel, Field
from typing import List
from langchain_openai import ChatOpenAI


class SubTask(BaseModel):
    sub_query: str = Field(description="Specific research sub-query to run.")
    source: str = Field(
        description="Source engine to target: 'web' (Tavily) or 'arxiv' (ArXiv API)."
    )


class ResearchPlan(BaseModel):
    tasks: List[SubTask] = Field(
        description="Decomposed checklist of queries to cover."
    )


class PlannerAgent:
    def __init__(self):
        openai_api_key = os.getenv("OPENAI_API_KEY") or "mock-key-for-import-validation"
        self.llm = ChatOpenAI(
            model="gpt-4o-mini", temperature=0.1, api_key=openai_api_key
        )
        self.structured_llm = self.llm.with_structured_output(ResearchPlan)

    def decompose_query(self, query: str) -> dict:
        """Decomposes a complex research query into sub-queries."""
        system_msg = (
            "You are an expert planning agent. Your role is to break down a complex, high-level research query "
            "into 3 to 5 clear, actionable sub-queries. For each sub-query, select the most appropriate source "
            "type:\n"
            "- 'arxiv' for academic, scientific, or highly technical research papers.\n"
            "- 'web' for general web search, current news, product specs, or commercial details.\n"
            "Ensure the sub-queries comprehensively cover all aspects of the original query."
        )
        try:
            plan = self.structured_llm.invoke(
                [("system", system_msg), ("user", f"Decompose this query: {query}")]
            )
            tasks_list = []
            for t in plan.tasks:
                tasks_list.append(
                    {"sub_query": t.sub_query, "source": t.source, "status": "pending"}
                )
            return {"tasks": tasks_list}
        except Exception as e:
            print(f"Error in PlannerAgent: {e}")
            # Safe fallback: return a default task containing the original query targeting web
            return {
                "tasks": [{"sub_query": query, "source": "web", "status": "pending"}]
            }
