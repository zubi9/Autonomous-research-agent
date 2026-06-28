"""
Short-term Memory
Handles session-specific state, transient working context, and caching in Redis.
"""


class ShortTermMemory:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url

    def save_session_state(self, session_id: str, state: dict):
        """Saves transient agent state for a session."""
        pass

    def get_session_state(self, session_id: str) -> dict:
        """Retrieves transient agent state."""
        return {}
