"""
API Routes
Defines endpoints for research tasks, background jobs, and reports.
"""

from fastapi import APIRouter, BackgroundTasks
from api.schemas import ResearchRequest, ResearchResponse, StatusResponse

router = APIRouter()


@router.post("/research", response_model=ResearchResponse)
async def trigger_research(payload: ResearchRequest, background_tasks: BackgroundTasks):
    """Trigger research job inside the workflow engine."""
    # In a real setup, we would trigger LangGraph async and return a task ID
    return {"task_id": "temp-task-id", "status": "queued"}


@router.get("/status/{task_id}", response_model=StatusResponse)
async def get_task_status(task_id: str):
    """Get status of a running research process."""
    return {"task_id": task_id, "status": "running", "progress": 0.5}


@router.get("/report/{task_id}")
async def get_final_report(task_id: str):
    """Retrieve the final synthesized report."""
    return {"task_id": task_id, "report": "# Sample Report"}
