from typing import Any, Dict, List, Tuple

from .engine import ToolRegistry


def split_text_tool(state: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Split raw text into chunks of roughly N words.

    Expects:
        state["text"]: str
        state["chunk_size"]: int (optional, default 80)

    Produces:
        state["chunks"]: List[str]
    """
    text = state.get("text", "")
    chunk_size = state.get("chunk_size", config.get("chunk_size", 80))

    words = text.split()
    chunks: List[str] = []
    for i in range(0, len(words), chunk_size):
        chunk_words = words[i: i + chunk_size]
        chunks.append(" ".join(chunk_words))

    return {"chunks": chunks}


def summarize_chunk(chunk: str, max_words: int) -> str:
    """
    Very naive 'summary':
      - Take the first max_words words.
      - This keeps it strictly rule-based (no ML).
    """
    words = chunk.split()
    return " ".join(words[:max_words])


def summarize_chunks_tool(state: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a small summary for each chunk.

    Expects:
        state["chunks"]: List[str]
        state["per_chunk_summary_size"]: int (optional, default 30)

    Produces:
        state["chunk_summaries"]: List[str]
    """
    chunks: List[str] = state.get("chunks", [])
    per_chunk_summary_size = state.get(
        "per_chunk_summary_size",
        config.get("per_chunk_summary_size", 30),
    )

    summaries = [
        summarize_chunk(chunk, per_chunk_summary_size) for chunk in chunks
    ]

    return {"chunk_summaries": summaries}


def merge_summaries_tool(state: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge chunk summaries into a single long summary.

    Expects:
        state["chunk_summaries"]: List[str]

    Produces:
        state["summary"]: str
    """
    chunk_summaries: List[str] = state.get("chunk_summaries", [])
    summary = " ".join(chunk_summaries)
    return {"summary": summary}


def refine_summary_tool(state: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Refine / shorten the summary heuristically.

    Strategy:
      - If summary is longer than max_summary_words,
        keep only the first max_summary_words words.

    Expects:
        state["summary"]: str
        state["max_summary_words"]: int (optional, default 80)

    Produces (updated):
        state["summary"]: str
    """
    summary: str = state.get("summary", "")
    max_words = state.get("max_summary_words", config.get("max_summary_words", 80))

    words = summary.split()
    if len(words) <= max_words:
        # Nothing to change
        return {}

    shortened = " ".join(words[:max_words])
    return {"summary": shortened}


def evaluate_summary_tool(state: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate current summary length.

    Expects:
        state["summary"]: str

    Produces:
        state["summary_length"]: int
    """
    summary: str = state.get("summary", "")
    length = len(summary.split())
    return {"summary_length": length}


def register_default_tools(registry: ToolRegistry) -> None:
    """Register all tools that can be used by graphs."""
    registry.register("split_text", split_text_tool)
    registry.register("summarize_chunks", summarize_chunks_tool)
    registry.register("merge_summaries", merge_summaries_tool)
    registry.register("refine_summary", refine_summary_tool)
    registry.register("evaluate_summary", evaluate_summary_tool)
