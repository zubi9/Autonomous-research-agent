"""
Pydantic Schemas
Defines request and response schemas for FastAPI validation.
"""

from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    query: str = Field(
        ...,
        json_schema_extra={
            "example": "What are the recent breakthroughs in room temperature superconductivity?"
        },
    )
    max_depth: int | None = Field(default=3, description="Maximum sub-query depth")
    sources: list[str] | None = Field(
        default=["web", "arxiv"], description="Sources to query"
    )


class ResearchResponse(BaseModel):
    task_id: str
    status: str


class StatusResponse(BaseModel):
    task_id: str
    status: str
    progress: float
    error: str | None = None
