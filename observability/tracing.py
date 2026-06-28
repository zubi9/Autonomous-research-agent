"""
Tracing Setup
Configures tracing instrumentation with LangSmith or Arize Phoenix.
"""

import os


def setup_tracing():
    """Instruments OpenTelemetry / LangSmith environment variables."""
    if os.getenv("LANGCHAIN_TRACING_V2") == "true":
        print("Tracing enabled: LangSmith")
    elif os.getenv("PHOENIX_COLLECTOR_ENDPOINT"):
        print("Tracing enabled: Arize Phoenix")
    else:
        print("Tracing is currently disabled.")
