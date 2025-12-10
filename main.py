from typing import Any, Dict

from fastapi import FastAPI, HTTPException

from .engine import GraphEngine, ToolRegistry
from .models import (
    GraphCreateRequest,
    GraphCreateResponse,
    GraphRunRequest,
    GraphRunResponse,
    RunStateResponse,
)
from . import tools


app = FastAPI(title="Minimal Agent Workflow Engine")

# --- Tool registry and engine setup ---

tool_registry = ToolRegistry()

# Register tools for Option B workflow
tool_registry.register("split_text", tools.split_text)
tool_registry.register("generate_summaries", tools.generate_summaries)
tool_registry.register("merge_summaries", tools.merge_summaries)
tool_registry.register("refine_summary", tools.refine_summary)

engine = GraphEngine(tool_registry=tool_registry)


@app.post("/graph/create", response_model=GraphCreateResponse)
def create_graph(req: GraphCreateRequest) -> GraphCreateResponse:
    """
    Create a new graph definition.

    Example body for Option B (Summarization + Refinement):

    {
      "nodes": ["split_text", "generate_summaries", "merge_summaries", "refine_summary"],
      "start_node": "split_text",
      "edges": {
        "split_text":        {"next": "generate_summaries"},
        "generate_summaries":{"next": "merge_summaries"},
        "merge_summaries":   {"next": "refine_summary"},
        "refine_summary": {
          "condition_key": "is_summary_short_enough",
          "on_true": "end",
          "on_false": "refine_summary"
        }
      }
    }
    """
    try:
        graph_id = engine.create_graph(
            nodes=req.nodes,
            start_node=req.start_node,
            edges=req.edges,
        )
        return GraphCreateResponse(graph_id=graph_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.post("/graph/run", response_model=GraphRunResponse)
def run_graph(req: GraphRunRequest) -> GraphRunResponse:
    """
    Run a previously created graph with an initial state.

    Example body for Option B:

    {
      "graph_id": "<graph_id_from_create>",
      "initial_state": {
        "text": "Long article text here...",
        "chunk_size": 60,
        "per_chunk_summary_words": 25,
        "summary_limit_words": 120
      }
    }
    """
    try:
        run = engine.run_graph(req.graph_id, req.initial_state)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    return GraphRunResponse(
        run_id=run.run_id,
        final_state=run.state,
        log=run.log,
    )


@app.get("/graph/state/{run_id}", response_model=RunStateResponse)
def get_run_state(run_id: str) -> RunStateResponse:
    """
    Get current or final state of a workflow run.
    """
    try:
        run = engine.get_run(run_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    return RunStateResponse(
        run_id=run.run_id,
        status=run.status,
        current_node=run.current_node,
        state=run.state,
        log=run.log,
    )


@app.get("/")
def root() -> Dict[str, Any]:
    return {"message": "Minimal agent workflow engine is running."}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

