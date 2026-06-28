"""
Embeddings Wrapper
Abstract wrapper interface for text embedding models (Gemini, OpenAI, HuggingFace).
"""


class EmbeddingsWrapper:
    def __init__(self, model_name: str):
        self.model_name = model_name

    def embed_text(self, text: str) -> list[float]:
        """Generates a vector embedding for the input text."""
        return []
