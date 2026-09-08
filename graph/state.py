"""
Graph State Schema
Defines the structure of the data passed along graph execution edges.
"""

from typing import Any, TypedDict


class ResearchState(TypedDict):
    query: str
    plan: dict[str, Any]
    tasks_pending: list[dict[str, Any]]
    documents: list[dict[str, Any]]
    summaries: list[str]
    citations: list[dict[str, Any]]
    report: str
    metadata: dict[str, Any]
