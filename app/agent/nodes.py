# app/agent/nodes.py

from typing import Dict, Any, List
from app.agent.llm import ask_llm
from app.agent.rag import retrieve_context



async def planner_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Planner: uses LLM to break the user query into 3–5 subtasks.
    """
    query = state["query"]

    prompt = f"""
    You are a planning agent.

    Break the following task into 3–5 clear, concise subtasks.
    Return ONLY bullet points, one per line.

    Task: {query}
    """

    raw = ask_llm(prompt)

    subtasks: List[str] = [
        line.strip("-• ").strip()
        for line in raw.splitlines()
        if line.strip()
    ]

    state["subtasks"] = subtasks
    return state


async def researcher_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Researcher: placeholder for now.
    Later we will plug in real web search.
    For now, we just simulate research text per subtask.
    """
    subtasks: List[str] = state.get("subtasks", [])
    results: List[str] = []

    for task in subtasks:
        # Placeholder research – will be replaced with real search API
        results.append(f"Notes: key ideas, definitions and examples about: {task}")

    state["results"] = results
    return state


async def summarizer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    query = state["query"]

    # Retrieve document context
    rag_context = retrieve_context(query)
    context_length = len(rag_context.strip())

    # Threshold: 500 chars = sufficient document content for strict mode
    # Below this, LLM can supplement with its own knowledge
    use_strict_mode = context_length >= 500

    if use_strict_mode:
        # 🔒 STRICT RAG MODE
        prompt = f"""
You are a retrieval-augmented assistant.

Answer the question using ONLY the information provided
in the DOCUMENT CONTEXT below.

DOCUMENT CONTEXT:
{rag_context}

Rules:
- Use ONLY the document content.
- Do NOT use prior knowledge.
- Do NOT infer beyond the text.
- If the answer is not present, say:
  "The provided documents do not contain enough information to answer this question."

Question:
{query}
"""
    else:
        # 🔓 HYBRID MODE (RAG + general knowledge)
        prompt = f"""
You are a helpful assistant.

Answer the question using:
1. The document context (if relevant)
2. General knowledge (if needed)

DOCUMENT CONTEXT (may be short or partial):
{rag_context}

WEB RESEARCH:
{web_text}

Rules:
- Prefer document context when available.
- You may use general knowledge if the document is insufficient.
- Clearly explain the answer.
- Keep it concise and clear.

Question:
{query}
"""

    summary = ask_llm(prompt)
    state["summary"] = summary
    state["rag_mode"] = "strict" if use_strict_mode else "hybrid"

    return state


async def report_writer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Report Writer: uses LLM to generate a polished, nicely formatted Markdown report.
    """
    query: str = state["query"]
    summary: str = state.get("summary", "")

    prompt = f"""
You are a professional technical writer.

Write a clear, well-formatted Markdown report based on the following:

Task / Query:
{query}

Bullet-point Summary of Key Points:
{summary}

Follow these rules strictly:
- Start with a single H1 title.
- Then use exactly these sections:
  ## Executive Summary
  ## Key Points
  ## Practical Tips / Recommendations
- Use bullet points where appropriate.
- Keep the report under 500 words.
- Do NOT include the characters "\\n" in the text. Use real new lines instead.
- Output ONLY valid Markdown. No extra commentary.
"""

    report = ask_llm(prompt)

    # In case the model still returns any literal "\n", convert them to real newlines
    report = report.replace("\\n", "\n").strip()

    state["report"] = report
    return state




