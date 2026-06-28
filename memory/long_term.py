"""
Long-term Memory
Manages document embeddings and retrieval in Qdrant vector database.
"""


class LongTermMemory:
    def __init__(self, qdrant_url: str):
        self.qdrant_url = qdrant_url

    def store_document(self, collection_name: str, text: str, metadata: dict):
        """Embeds and stores text into Qdrant."""
        pass

    def retrieve_relevant(
        self, collection_name: str, query_vector: list, limit: int = 5
    ):
        """Performs vector similarity search."""
        return []
