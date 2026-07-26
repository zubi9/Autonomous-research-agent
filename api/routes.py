import time
import uuid
from fastapi import APIRouter, BackgroundTasks, HTTPException
from api.schemas import ResearchRequest, ResearchResponse, StatusResponse
from memory.short_term import ShortTermMemory
from graph.workflow import create_research_graph
from graph.state import ResearchState
from observability.metrics import track_run_metrics

router = APIRouter()
redis_memory = ShortTermMemory()
graph = create_research_graph()


def run_research_task(task_id: str, query: str):
    """Background worker task to execute the LangGraph research workflow."""
    print(f"Background task starting for task_id: {task_id}")
    redis_memory.save_session_state(
        task_id, {"status": "running", "progress": 0.2, "query": query}
    )

    start_time = time.time()
    try:
        initial_state = ResearchState(
            query=query,
            plan={},
            tasks_pending=[],
            documents=[],
            summaries=[],
            citations=[],
            report="",
            metadata={"session_id": task_id},
        )

        # Execute the compiled LangGraph
        result = graph.invoke(initial_state)
        report = result.get("report", "")

        elapsed = time.time() - start_time

        # Track Prometheus metrics
        track_run_metrics(
            model="gpt-4o",
            prompt_tokens=15000,
            completion_tokens=4000,
            latency_seconds=elapsed,
        )

        # Save completed state to cache
        redis_memory.save_session_state(
            task_id,
            {
                "status": "completed",
                "progress": 1.0,
                "query": query,
                "report": report,
                "citations": result.get("citations", []),
                "summaries": result.get("summaries", []),
            },
        )
        print(f"Background task finished successfully for task_id: {task_id}")
    except Exception as e:
        print(f"Error in background task for task_id {task_id}: {e}")
        redis_memory.save_session_state(
            task_id,
            {"status": "failed", "progress": 0.0, "query": query, "error": str(e)},
        )


@router.post("/research", response_model=ResearchResponse)
async def trigger_research(payload: ResearchRequest, background_tasks: BackgroundTasks):
    """Trigger a new research workflow task in the background."""
    task_id = str(uuid.uuid4())
    redis_memory.save_session_state(
        task_id, {"status": "queued", "progress": 0.0, "query": payload.query}
    )

    background_tasks.add_task(run_research_task, task_id, payload.query)

    return {"task_id": task_id, "status": "queued"}


@router.get("/status/{task_id}", response_model=StatusResponse)
async def get_task_status(task_id: str):
    """Get the current progress status of a running task."""
    state = redis_memory.get_session_state(task_id)
    if not state:
        raise HTTPException(status_code=404, detail="Task not found.")

    return {
        "task_id": task_id,
        "status": state.get("status", "unknown"),
        "progress": state.get("progress", 0.0),
        "error": state.get("error"),
    }


@router.get("/report/{task_id}")
async def get_final_report(task_id: str):
    """Retrieve the synthesized report for a completed task."""
    state = redis_memory.get_session_state(task_id)
    if not state:
        raise HTTPException(status_code=404, detail="Task not found.")

    if state.get("status") != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Report is not ready. Current status: {state.get('status')}",
        )

    return {
        "task_id": task_id,
        "report": state.get("report", ""),
        "citations": state.get("citations", []),
    }
