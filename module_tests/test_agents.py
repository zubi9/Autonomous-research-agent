"""Real-data smoke tests for the agent modules.

These tests exercise the planner, researcher, and writer agents with live tool
calls when the required environment variables are available.
"""

from __future__ import annotations

import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.planner import PlannerAgent
from agents.researcher import ResearcherAgent
from agents.writer import WriterAgent


class AgentSmokeTests(unittest.TestCase):
    def test_planner_agent_fallback(self) -> None:
        agent = PlannerAgent()
        plan = agent.decompose_query("latest room temperature superconductivity news")

        self.assertIn("tasks", plan)
        self.assertTrue(plan["tasks"], "Planner should return at least one task")

    def test_researcher_agent_with_web_source(self) -> None:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            self.skipTest(
                "TAVILY_API_KEY is not set; skipping live researcher web test"
            )

        agent = ResearcherAgent()
        result = agent.execute_task("room temperature superconductivity", "web")

        self.assertIn("summary", result)
        self.assertTrue(
            result["citations"] or result["documents"],
            "Researcher should collect documents or citations",
        )

    def test_writer_agent_synthesizes_report(self) -> None:
        agent = WriterAgent()
        report = agent.synthesize_report(
            "room temperature superconductivity",
            ["A recent breakthrough was reported."],
            [{"title": "Example Source", "url": "https://example.com"}],
        )

        self.assertIn("room temperature superconductivity", report)
        self.assertIn("References", report)


if __name__ == "__main__":
    unittest.main(verbosity=2)
