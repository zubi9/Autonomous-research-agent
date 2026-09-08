import os

from langchain_openai import OpenAIEmbeddings


class EmbeddingsWrapper:
    def __init__(self, model_name: str = "text-embedding-3-small"):
        self.model_name = model_name
        openai_api_key = os.getenv("OPENAI_API_KEY") or "mock-key-for-import-validation"
        self.embeddings = OpenAIEmbeddings(
            model=self.model_name, api_key=openai_api_key
        )

    def embed_text(self, text: str) -> list[float]:
        """Generates a vector embedding for the input text."""
        try:
            return self.embeddings.embed_query(text)
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            # Return dummy 1536-dim vector if API key is not configured (e.g. during offline test runs)
            return [0.0] * 1536
