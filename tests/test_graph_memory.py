import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Ensure root folder is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph.state import ResearchState
from graph.workflow import create_research_graph
from memory.long_term import LongTermMemory
from memory.short_term import ShortTermMemory


class TestGraphMemory(unittest.TestCase):
    @patch("memory.short_term.redis.from_url")
    def test_short_term_memory_saves_and_reads_state(self, mock_redis_from_url):
        mock_client = MagicMock()
        mock_redis_from_url.return_value = mock_client
        mock_client.get.return_value = (
            '{"query": "superconductivity", "report": "empty"}'
        )

        memory = ShortTermMemory(redis_url="redis://localhost:6379/0")

        memory.save_session_state("session-123", {"query": "superconductivity"})
        mock_client.set.assert_called_once()

        state = memory.get_session_state("session-123")
        self.assertEqual(state["query"], "superconductivity")
        self.assertEqual(state["report"], "empty")

    @patch("memory.short_term.redis.from_url")
    def test_short_term_memory_returns_empty_state_when_client_unavailable(
        self, mock_redis_from_url
    ):
        mock_redis_from_url.side_effect = RuntimeError("redis unavailable")

        memory = ShortTermMemory(redis_url="redis://localhost:6379/0")

        memory.save_session_state("session-123", {"query": "superconductivity"})
        self.assertEqual(memory.get_session_state("session-123"), {})
        self.assertIsNone(memory.client)

    @patch("memory.long_term.QdrantClient")
    @patch("memory.long_term.EmbeddingsWrapper")
    def test_long_term_memory_creates_collection_and_retrieves_documents(
        self, mock_embeddings_wrapper, mock_qdrant_client
    ):
        mock_client = MagicMock()
        mock_qdrant_client.return_value = mock_client
        mock_embeddings = MagicMock()
        mock_embeddings_wrapper.return_value = mock_embeddings
        mock_embeddings.embed_text.return_value = [0.1] * 1536

        mock_collections_res = MagicMock()
        mock_collections_res.collections = []
        mock_client.get_collections.return_value = mock_collections_res

        memory = LongTermMemory(qdrant_url="http://localhost:6333")

        memory.store_document(
            "test_collection",
            "Sample research article body",
            {"url": "https://example.com"},
        )

        mock_client.create_collection.assert_called_once()
        mock_client.upsert.assert_called_once()

        mock_client.search.return_value = [
            MagicMock(payload={"text": "Retrieved doc text"}, score=0.92)
        ]

        results = memory.retrieve_relevant("test_collection", "Sample query", limit=2)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["text"], "Retrieved doc text")
        self.assertEqual(results[0]["score"], 0.92)

    def test_long_term_memory_returns_empty_results_when_client_unavailable(self):
        with patch("memory.long_term.QdrantClient", side_effect=RuntimeError("boom")):
            memory = LongTermMemory(qdrant_url="http://localhost:6333")
            self.assertEqual(memory.retrieve_relevant("test_collection", "query"), [])
            memory.store_document("test_collection", "text")

        self.assertIsNone(memory.client)

    @patch("graph.nodes.PlannerAgent")
    @patch("graph.nodes.ResearcherAgent")
    @patch("graph.nodes.WriterAgent")
    def test_graph_workflow_routes_across_nodes(
        self, mock_writer, mock_researcher, mock_planner
    ):
        planner_inst = MagicMock()
        planner_inst.decompose_query.return_value = {
            "tasks": [{"sub_query": "subquery 1", "source": "web", "status": "pending"}]
        }
        mock_planner.return_value = planner_inst

        researcher_inst = MagicMock()
        researcher_inst.execute_task.return_value = {
            "summary": "This is a summary of web research.",
            "citations": [
                {
                    "title": "Web citation",
                    "url": "https://example.com/1",
                    "source": "web",
                }
            ],
            "documents": [
                {
                    "title": "Web doc",
                    "text": "web doc content",
                    "url": "https://example.com/1",
                    "source": "web",
                }
            ],
        }
        mock_researcher.return_value = researcher_inst

        writer_inst = MagicMock()
        writer_inst.synthesize_report.return_value = (
            "# Final Integrated Research Report"
        )
        mock_writer.return_value = writer_inst

        graph = create_research_graph()
        self.assertIsNotNone(graph)

        initial_state = ResearchState(
            query="advancements in warm superconductivity",
            plan={},
            tasks_pending=[],
            documents=[],
            summaries=[],
            citations=[],
            report="",
            metadata={},
        )

        result = graph.invoke(initial_state)

        self.assertEqual(result["report"], "# Final Integrated Research Report")
        self.assertEqual(result["summaries"], ["This is a summary of web research."])
        self.assertEqual(result["tasks_pending"], [])


if __name__ == "__main__":
    unittest.main()
