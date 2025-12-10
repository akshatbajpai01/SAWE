from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

from .models import NodeLogEntry


ToolFunc = Callable[[Dict[str, Any]], Dict[str, Any]]


@dataclass
class Graph:
    graph_id: str
    nodes: List[str]
    start_node: str
    edges: Dict[str, Dict[str, Any]]  # flexible edge definition


@dataclass
class RunRecord:
    run_id: str
    graph_id: str
    status: str  # "running" | "completed" | "error"
    current_node: Optional[str]
    state: Dict[str, Any] = field(default_factory=dict)
    log: List[NodeLogEntry] = field(default_factory=list)
    error_message: Optional[str] = None


class ToolRegistry:
    """
    Simple tool registry: node_name -> Python function
    """

    def __init__(self) -> None:
        self._tools: Dict[str, ToolFunc] = {}

    def register(self, name: str, func: ToolFunc) -> None:
        self._tools[name] = func

    def get(self, name: str) -> ToolFunc:
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' is not registered")
        return self._tools[name]


class GraphEngine:
    """
    In-memory graph + run engine.
    """

    def __init__(self, tool_registry: ToolRegistry) -> None:
        self.tool_registry = tool_registry
        self.graphs: Dict[str, Graph] = {}
        self.runs: Dict[str, RunRecord] = {}

    # -------- Graph management --------

    def create_graph(
        self,
        nodes: List[str],
        start_node: str,
        edges: Dict[str, Dict[str, Any]],
    ) -> str:
        if start_node not in nodes:
            raise ValueError("start_node must be one of the nodes")

        graph_id = str(uuid4())
        graph = Graph(
            graph_id=graph_id,
            nodes=nodes,
            start_node=start_node,
            edges=edges,
        )
        self.graphs[graph_id] = graph
        return graph_id

    # -------- Execution --------

    def run_graph(self, graph_id: str, initial_state: Dict[str, Any]) -> RunRecord:
        if graph_id not in self.graphs:
            raise KeyError(f"Graph '{graph_id}' not found")

        graph = self.graphs[graph_id]
        run_id = str(uuid4())
        run = RunRecord(
            run_id=run_id,
            graph_id=graph_id,
            status="running",
            current_node=graph.start_node,
            state=dict(initial_state),
            log=[],
        )
        self.runs[run_id] = run

        try:
            self._execute_run(graph, run)
            run.status = "completed"
            run.current_node = None
        except Exception as exc:  # noqa: BLE001 - simple assignment
            run.status = "error"
            run.error_message = str(exc)

        return run

    def _execute_run(self, graph: Graph, run: RunRecord) -> None:
        """
        Core execution loop with basic branching + looping.
        Edges format for a node can be:

        1. Simple linear:
           {"next": "some_node"}

        2. Conditional:
           {
              "condition_key": "is_summary_short_enough",
              "on_true": "end",
              "on_false": "refine_summary"
           }

        'end' or missing next node = stop.
        """
        max_steps = 1000  # safety for infinite loops
        current = graph.start_node
        steps = 0

        while current and steps < max_steps:
            run.current_node = current
            tool = self.tool_registry.get(current)

            # Execute node
            new_state = tool(run.state) or {}
            # Merge new keys into shared state
            run.state.update(new_state)

            # Log snapshot after this node
            run.log.append(NodeLogEntry(node=current, state=dict(run.state)))

            # Decide next node
            edge_cfg = graph.edges.get(current, {})
            next_node = self._resolve_next_node(edge_cfg, run.state)

            if not next_node or next_node == "end":
                break

            current = next_node
            steps += 1

    @staticmethod
    def _resolve_next_node(edge_cfg: Dict[str, Any], state: Dict[str, Any]) -> Optional[str]:
        if not edge_cfg:
            return None

        # Conditional routing
        condition_key = edge_cfg.get("condition_key")
        if condition_key is not None:
            flag = bool(state.get(condition_key))
            return edge_cfg["on_true"] if flag else edge_cfg["on_false"]

        # Simple linear edge
        return edge_cfg.get("next")

    # -------- State inspection --------

    def get_run(self, run_id: str) -> RunRecord:
        if run_id not in self.runs:
            raise KeyError(f"Run '{run_id}' not found")
        return self.runs[run_id]
