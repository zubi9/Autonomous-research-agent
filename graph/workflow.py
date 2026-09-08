from langgraph.graph import END, StateGraph

from graph.nodes import planner_node, researcher_node, writer_node
from graph.state import ResearchState


def create_research_graph():
    # Initialize the graph with the state schema
    workflow = StateGraph(ResearchState)

    # Add agent nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("writer", writer_node)

    # Set entry point
    workflow.set_entry_point("planner")

    # Add edges
    workflow.add_conditional_edges(
        "planner",
        lambda state: "researcher" if state.get("tasks_pending") else "writer",
        {"researcher": "researcher", "writer": "writer"},
    )
    workflow.add_edge("researcher", "planner")
    workflow.add_edge("writer", END)

    return workflow.compile()
