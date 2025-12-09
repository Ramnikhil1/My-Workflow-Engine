from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, List
from uuid import uuid4
import copy

from .models import EdgeConfig, NodeConfig, StepLog


@dataclass
class Node:
    id: str
    tool: str
    config: Dict[str, Any]


@dataclass
class Edge:
    from_node: str
    to_node: Optional[str] = None

    condition_key: Optional[str] = None
    condition_op: Optional[str] = None
    condition_value: Any = None
    true_target: Optional[str] = None
    false_target: Optional[str] = None


@dataclass
class Graph:
    id: str
    name: str
    start_node: str
    nodes: Dict[str, Node]
    edges: Dict[str, Edge]  # keyed by from_node


@dataclass
class Run:
    id: str
    graph_id: str
    status: str
    current_node: Optional[str]
    state: Dict[str, Any]
    log: List[StepLog]


class ToolRegistry:
    """
    Simple registry: maps string names to Python callables.

    Tool signature:
        def tool(state: dict, config: dict) -> dict:
            # read/modify state and return updates
    """

    def __init__(self) -> None:
        self._tools: Dict[str, Callable[[Dict[str, Any], Dict[str, Any]], Dict[str, Any]]] = {}

    def register(self, name: str, func: Callable[[Dict[str, Any], Dict[str, Any]], Dict[str, Any]]) -> None:
        self._tools[name] = func

    def get(self, name: str) -> Callable[[Dict[str, Any], Dict[str, Any]], Dict[str, Any]]:
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' is not registered.")
        return self._tools[name]

    def list_tools(self) -> List[str]:
        return list(self._tools.keys())


class GraphEngine:
    """
    Minimal in-memory graph engine.

    Responsibilities:
      - Store graphs
      - Store runs
      - Execute a graph step-by-step with shared state
      - Support simple branching and loops
    """

    def __init__(self, tool_registry: ToolRegistry) -> None:
        self.tool_registry = tool_registry
        self.graphs: Dict[str, Graph] = {}
        self.runs: Dict[str, Run] = {}

    # ---------- Graph management ----------

    def create_graph(self, name: str, start_node: str,
                     nodes_cfg: List[NodeConfig],
                     edges_cfg: List[EdgeConfig]) -> str:
        nodes: Dict[str, Node] = {}
        edges: Dict[str, Edge] = {}

        for nc in nodes_cfg:
            nodes[nc.id] = Node(id=nc.id, tool=nc.tool, config=nc.config)

        for ec in edges_cfg:
            edges[ec.from_node] = Edge(
                from_node=ec.from_node,
                to_node=ec.to_node,
                condition_key=ec.condition_key,
                condition_op=ec.condition_op,
                condition_value=ec.condition_value,
                true_target=ec.true_target,
                false_target=ec.false_target,
            )

        graph_id = str(uuid4())
        graph = Graph(
            id=graph_id,
            name=name,
            start_node=start_node,
            nodes=nodes,
            edges=edges,
        )
        self.graphs[graph_id] = graph
        return graph_id

    def get_graph(self, graph_id: str) -> Graph:
        if graph_id not in self.graphs:
            raise KeyError(f"Graph '{graph_id}' not found.")
        return self.graphs[graph_id]

    # ---------- Run / Execution ----------

    @staticmethod
    def _compare(lhs: Any, op: str, rhs: Any) -> bool:
        if op == "gt":
            return lhs > rhs
        if op == "ge":
            return lhs >= rhs
        if op == "lt":
            return lhs < rhs
        if op == "le":
            return lhs <= rhs
        if op == "eq":
            return lhs == rhs
        if op == "ne":
            return lhs != rhs
        raise ValueError(f"Unsupported operator '{op}'.")

    def _next_node_id(self, graph: Graph, current_node_id: str, state: Dict[str, Any]) -> Optional[str]:
        edge = graph.edges.get(current_node_id)
        if edge is None:
            # No outgoing edge → terminal node
            return None

        # No condition → simple linear edge
        if edge.condition_key is None or edge.condition_op is None:
            return edge.to_node

        # Conditional edge
        value = state.get(edge.condition_key)
        result = self._compare(value, edge.condition_op, edge.condition_value)
        return edge.true_target if result else edge.false_target

    def run_graph(self, graph_id: str, initial_state: Dict[str, Any],
                  max_steps: int = 100) -> Run:
        graph = self.get_graph(graph_id)

        run_id = str(uuid4())
        state: Dict[str, Any] = dict(initial_state)  # shallow copy
        logs: List[StepLog] = []

        current_node_id: Optional[str] = graph.start_node
        status = "running"

        for step_index in range(max_steps):
            if current_node_id is None:
                status = "completed"
                break

            node = graph.nodes.get(current_node_id)
            if node is None:
                status = "failed"
                break

            tool = self.tool_registry.get(node.tool)
            # Call tool, merge returned updates into state
            updates = tool(state, node.config) or {}
            state.update(updates)

            logs.append(
                StepLog(
                    step_index=step_index,
                    node_id=node.id,
                    tool=node.tool,
                    state_snapshot=copy.deepcopy(state),
                )
            )

            next_node_id = self._next_node_id(graph, current_node_id, state)
            current_node_id = next_node_id

        else:
            # If we exit by hitting max_steps
            status = "failed"

        run = Run(
            id=run_id,
            graph_id=graph_id,
            status=status,
            current_node=current_node_id,
            state=state,
            log=logs,
        )
        self.runs[run_id] = run
        return run

    def get_run(self, run_id: str) -> Run:
        if run_id not in self.runs:
            raise KeyError(f"Run '{run_id}' not found.")
        return self.runs[run_id]
