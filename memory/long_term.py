import os
import uuid

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams

from memory.embeddings import EmbeddingsWrapper


class LongTermMemory:
    def __init__(self, qdrant_url: str = None):
        self.qdrant_url = qdrant_url or os.getenv("QDRANT_URL", "http://localhost:6333")
        try:
            self.client = QdrantClient(url=self.qdrant_url)
        except Exception as e:
            print(f"Failed to connect to Qdrant at {self.qdrant_url}: {e}")
            self.client = None
        self.embeddings = EmbeddingsWrapper()

    def _ensure_collection(self, collection_name: str, vector_size: int = 1536):
        if not self.client:
            return
        try:
            collections = self.client.get_collections()
            exist = any(col.name == collection_name for col in collections.collections)
            if not exist:
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=vector_size, distance=Distance.COSINE
                    ),
                )
        except Exception as e:
            print(f"Error ensuring Qdrant collection '{collection_name}' exists: {e}")

    def store_document(self, collection_name: str, text: str, metadata: dict = None):
        """Embeds and stores text into Qdrant."""
        if not self.client:
            print("Qdrant client not available. Skipping store.")
            return
        try:
            self._ensure_collection(collection_name)
            vector = self.embeddings.embed_text(text)
            point_id = str(uuid.uuid4())
            self.client.upsert(
                collection_name=collection_name,
                points=[
                    PointStruct(
                        id=point_id,
                        vector=vector,
                        payload={"text": text, **(metadata or {})},
                    )
                ],
            )
        except Exception as e:
            print(f"Error storing document in Qdrant: {e}")

    def retrieve_relevant(
        self, collection_name: str, query_or_vector, limit: int = 5
    ) -> list[dict]:
        """Performs vector similarity search using either a text query or raw vector."""
        if not self.client:
            print("Qdrant client not available. Returning empty results.")
            return []
        try:
            self._ensure_collection(collection_name)
            if isinstance(query_or_vector, str):
                vector = self.embeddings.embed_text(query_or_vector)
            else:
                vector = query_or_vector

            results = self.client.search(
                collection_name=collection_name, query_vector=vector, limit=limit
            )
            retrieved = []
            for hit in results:
                retrieved.append(
                    {
                        "text": hit.payload.get("text", ""),
                        "score": hit.score,
                        "metadata": {
                            k: v for k, v in hit.payload.items() if k != "text"
                        },
                    }
                )
            return retrieved
        except Exception as e:
            print(f"Error retrieving relevant documents from Qdrant: {e}")
            return []
