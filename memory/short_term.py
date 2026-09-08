import json
import os

import redis


class ShortTermMemory:
    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        try:
            # decode_responses=True ensures we get back python strings instead of bytes
            self.client = redis.from_url(self.redis_url, decode_responses=True)
        except Exception as e:
            print(f"Failed to connect to Redis at {self.redis_url}: {e}")
            self.client = None

    def save_session_state(self, session_id: str, state: dict):
        """Saves transient agent state for a session."""
        if not self.client:
            print("Redis client is not available. Skipping save.")
            return
        try:
            serialized = json.dumps(state)
            self.client.set(f"session:{session_id}:state", serialized)
        except Exception as e:
            print(f"Error saving session state to Redis: {e}")

    def get_session_state(self, session_id: str) -> dict:
        """Retrieves transient agent state."""
        if not self.client:
            print("Redis client is not available. Returning empty state.")
            return {}
        try:
            data = self.client.get(f"session:{session_id}:state")
            if data:
                return json.loads(data)
        except Exception as e:
            print(f"Error retrieving session state from Redis: {e}")
        return {}
