"""
Pydantic Schemas
Defines request and response schemas for FastAPI validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class ResearchRequest(BaseModel):
    query: str = Field(
        ...,
        example="What are the recent breakthroughs in room temperature superconductivity?",
    )
    max_depth: Optional[int] = Field(default=3, description="Maximum sub-query depth")
    sources: Optional[List[str]] = Field(
        default=["web", "arxiv"], description="Sources to query"
    )


class ResearchResponse(BaseModel):
    task_id: str
    status: str


class StatusResponse(BaseModel):
    task_id: str
    status: str
    progress: float
    error: Optional[str] = None
