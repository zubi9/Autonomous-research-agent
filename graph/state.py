"""
Graph State Schema
Defines the structure of the data passed along graph execution edges.
"""

from typing import TypedDict, List, Dict, Any


class ResearchState(TypedDict):
    query: str
    plan: Dict[str, Any]
    tasks_pending: List[Dict[str, Any]]
    documents: List[Dict[str, Any]]
    summaries: List[str]
    citations: List[Dict[str, Any]]
    report: str
    metadata: Dict[str, Any]
