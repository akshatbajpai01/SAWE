from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class GraphCreateRequest(BaseModel):
    """
    Request body for /graph/create
    """
    nodes: List[str]
    start_node: str
    edges: Dict[str, Dict[str, Any]]


class GraphCreateResponse(BaseModel):
    graph_id: str


class GraphRunRequest(BaseModel):
    """
    Request body for /graph/run
    """
    graph_id: str
    initial_state: Dict[str, Any] = Field(default_factory=dict)


class NodeLogEntry(BaseModel):
    node: str
    state: Dict[str, Any]


class GraphRunResponse(BaseModel):
    run_id: str
    final_state: Dict[str, Any]
    log: List[NodeLogEntry]


class RunStateResponse(BaseModel):
    run_id: str
    status: str
    current_node: Optional[str]
    state: Dict[str, Any]
    log: List[NodeLogEntry]
