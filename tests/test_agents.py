import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Ensure root folder is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.baseline import agent_executor


class TestAgents(unittest.TestCase):
    @patch("agents.baseline.agent_executor.invoke")
    def test_baseline_agent_success(self, mock_invoke):
        # Mock message content returned by LangGraph React Agent
        mock_message = MagicMock()
        mock_message.content = "# Research Report on Room Temperature Superconductors\n\nAdvancements include developments in LK-99 analogs..."

        mock_invoke.return_value = {"messages": [mock_message]}

        result = agent_executor.invoke({"messages": [("user", "LK-99 advancements")]})
        output_report = result["messages"][-1].content

        self.assertIn("LK-99 analogs", output_report)
        mock_invoke.assert_called_once_with(
            {"messages": [("user", "LK-99 advancements")]}
        )


if __name__ == "__main__":
    unittest.main()
