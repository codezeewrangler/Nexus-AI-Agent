# app/agent/graph.py

from typing import Dict, Any, Tuple, Optional
from app.agent.nodes import (
    planner_node,
    researcher_node,
    summarizer_node,
    report_writer_node,
)


async def run_agent_graph(
    query: str,
    user_id: Optional[str],
    output_format: str
) -> Tuple[str, Dict[str, Any]]:

    state: Dict[str, Any] = {
        "query": query,
        "user_id": user_id,
        "output_format": output_format,
        "subtasks": [],
        "results": [],
        "summary": "",
        "report": "",
    }

    # Sequential pipeline (like a simple LangGraph workflow)
    state = await planner_node(state)
    state = await researcher_node(state)
    state = await summarizer_node(state)
    state = await report_writer_node(state)

    report = state["report"]
    meta = {
        "num_subtasks": len(state["subtasks"]),
        "num_results": len(state["results"]),
        "user_id": user_id,
    }
    return report, meta
