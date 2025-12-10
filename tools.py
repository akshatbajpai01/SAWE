from typing import Any, Dict, List


def _simple_chunk_text(text: str, chunk_size: int) -> List[str]:
    words = text.split()
    chunks: List[str] = []
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i : i + chunk_size]))
    return chunks


def split_text(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node 1: Split text into chunks.

    Expects:
      state["text"]: str
      state["chunk_size"]: int (optional, default=50)

    Produces:
      state["chunks"]: List[str]
    """
    text = state.get("text", "")
    chunk_size = int(state.get("chunk_size", 50))
    chunks = _simple_chunk_text(text, chunk_size)
    return {"chunks": chunks}


def generate_summaries(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node 2: Generate summaries for each chunk.

    Simple rule-based: take first N words of each chunk.

    Expects:
      state["chunks"]: List[str]
      state["per_chunk_summary_words"]: int (optional, default=20)

    Produces:
      state["summaries"]: List[str]
    """
    chunks = state.get("chunks", [])
    max_words = int(state.get("per_chunk_summary_words", 20))

    summaries: List[str] = []
    for chunk in chunks:
        words = chunk.split()
        summaries.append(" ".join(words[:max_words]))
    return {"summaries": summaries}


def merge_summaries(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node 3: Merge summaries into a single draft summary.

    Expects:
      state["summaries"]: List[str]

    Produces:
      state["draft_summary"]: str
    """
    summaries = state.get("summaries", [])
    draft = " ".join(summaries)
    return {"draft_summary": draft}


def refine_summary(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Final refinement step.
    - Takes the draft summary.
    - Trims it to the required word limit.
    - Marks whether summary is within the limit.
    """

    draft = state.get("draft_summary", "")
    limit = state.get("summary_limit_words", 40)

    # Split into words
    words = draft.split()

    # Apply limit
    final_summary = " ".join(words[:limit])

    # check if final summary fits
    is_short_enough = len(words) <= limit

    # Save into state
    state["final_summary"] = final_summary
    state["is_summary_short_enough"] = is_short_enough

    # clean final state format
    state = {
        "text": state.get("text"),
        "chunk_size": state.get("chunk_size"),
        "per_chunk_summary_words": state.get("per_chunk_summary_words"),
        "summary_limit_words": state.get("summary_limit_words"),
        "final_summary": final_summary,
        "is_summary_short_enough": is_short_enough,
        "chunks": state.get("chunks"),
        "summaries": state.get("summaries"),
        "draft_summary": draft
    }

    return state
