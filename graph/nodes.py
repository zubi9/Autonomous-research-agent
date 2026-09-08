from agents.planner import PlannerAgent
from agents.researcher import ResearcherAgent
from agents.writer import WriterAgent
from graph.state import ResearchState


def planner_node(state: ResearchState) -> dict:
    """Planner node logic to analyze and route research tasks."""
    print("Executing Planner Node...")
    query = state.get("query", "")

    # If plan already exists (e.g. we looped back), don't recreate it
    if state.get("plan") and state.get("plan").get("tasks"):
        print("Plan already exists. Skipping query decomposition.")
        return {}

    planner = PlannerAgent()
    plan = planner.decompose_query(query)
    tasks = plan.get("tasks", [])

    return {
        "plan": plan,
        "tasks_pending": tasks,
        "summaries": [],
        "documents": [],
        "citations": [],
    }


def researcher_node(state: ResearchState) -> dict:
    """Researcher node logic to search web/arxiv and fetch resources."""
    print("Executing Researcher Node...")
    tasks_pending = state.get("tasks_pending", [])

    if not tasks_pending:
        print("No pending tasks. Researcher exiting.")
        return {}

    # Process the first pending task
    current_task = tasks_pending[0]
    sub_query = current_task.get("sub_query")
    source = current_task.get("source")

    researcher = ResearcherAgent()
    result = researcher.execute_task(sub_query, source)

    # Update plan task status in state copy
    plan = state.get("plan", {})
    if "tasks" in plan:
        for t in plan["tasks"]:
            if t.get("sub_query") == sub_query:
                t["status"] = "completed"

    new_summaries = state.get("summaries", []) or []
    if result.get("summary"):
        new_summaries.append(result["summary"])

    new_docs = state.get("documents", []) or []
    if result.get("documents"):
        new_docs.extend(result["documents"])

    new_citations = state.get("citations", []) or []
    if result.get("citations"):
        new_citations.extend(result["citations"])

    return {
        "plan": plan,
        "tasks_pending": tasks_pending[1:],
        "summaries": new_summaries,
        "documents": new_docs,
        "citations": new_citations,
    }


def writer_node(state: ResearchState) -> dict:
    """Writer node logic to synthesize the final markdown/PDF report."""
    print("Executing Writer Node...")
    query = state.get("query", "")
    summaries = state.get("summaries", []) or []
    citations = state.get("citations", []) or []

    writer = WriterAgent()
    report = writer.synthesize_report(query, summaries, citations)

    return {"report": report}
