import os
import sys
import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

# Ensure root folder is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock redis module BEFORE importing FastAPI app to prevent connection errors
with patch("redis.from_url") as mock_redis:
    mock_redis.return_value = MagicMock()
    from api.main import app

from output.citation_manager import CitationManager
from output.formatter import ReportFormatter


class TestApiOutput(unittest.TestCase):
    @patch("api.routes.redis_memory")
    @patch("api.routes.BackgroundTasks.add_task")
    def test_trigger_research(self, mock_add_task, mock_redis_memory):
        client = TestClient(app)

        payload = {"query": "Superconductors breakthroughs"}
        response = client.post("/api/v1/research", json=payload)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("task_id", data)
        self.assertEqual(data["status"], "queued")
        mock_add_task.assert_called_once()
        mock_redis_memory.save_session_state.assert_called_once()

    @patch("api.routes.redis_memory")
    def test_status_endpoint(self, mock_redis_memory):
        client = TestClient(app)

        mock_redis_memory.get_session_state.return_value = {
            "status": "running",
            "progress": 0.5,
        }

        response = client.get("/api/v1/status/fake-task-id")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "running")
        self.assertEqual(data["progress"], 0.5)

    @patch("api.routes.redis_memory")
    def test_report_endpoint(self, mock_redis_memory):
        client = TestClient(app)

        mock_redis_memory.get_session_state.return_value = {
            "status": "completed",
            "progress": 1.0,
            "report": "# Complete Report",
            "citations": [],
        }

        response = client.get("/api/v1/report/fake-task-id")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["report"], "# Complete Report")

    def test_citation_manager_dedup(self):
        manager = CitationManager()
        cits = [
            {"title": "Source 1", "url": "https://example.com/1"},
            {"title": "Source 2", "url": "https://example.com/1"},
            {"title": "Source 3", "url": "https://example.com/2"},
        ]
        deduped = manager.deduplicate(cits)
        self.assertEqual(len(deduped), 2)

    @patch("output.citation_manager.requests.head")
    def test_citation_manager_confidence(self, mock_head):
        manager = CitationManager()

        mock_res = MagicMock()
        mock_res.status_code = 200
        mock_head.return_value = mock_res

        score_arxiv = manager.calculate_confidence(
            {"url": "https://arxiv.org/abs/2307.12008"}
        )
        self.assertGreaterEqual(score_arxiv, 0.90)

        score_edu = manager.calculate_confidence(
            {"url": "https://university.edu/paper"}
        )
        self.assertGreaterEqual(score_edu, 0.85)

    @patch("output.formatter.FPDF.output")
    def test_report_formatter_pdf(self, mock_fpdf_output):
        formatter = ReportFormatter()
        markdown = (
            "# Title\n\n## Subtitle\n- Bullet 1\n- Bullet 2\nNormal text goes here."
        )

        formatter.to_pdf(markdown, "dummy_report.pdf")
        mock_fpdf_output.assert_called_once_with("dummy_report.pdf")


if __name__ == "__main__":
    unittest.main()
