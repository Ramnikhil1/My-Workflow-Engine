from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel


class NodeConfig(BaseModel):
    """Configuration of a single node in a graph."""
    id: str
    tool: str
    config: Dict[str, Any] = {}


class EdgeConfig(BaseModel):
    """
    A single edge between nodes.

    Either:
      - simple linear: from_node -> to_node
      - or conditional: from_node -> (true_target / false_target)
        based on state[condition_key] (condition_op condition_value)
    """
    from_node: str
    to_node: Optional[str] = None

    # Conditional routing fields (optional)
    condition_key: Optional[str] = None
    condition_op: Optional[Literal["gt", "ge", "lt", "le", "eq", "ne"]] = None
    condition_value: Optional[Any] = None
    true_target: Optional[str] = None
    false_target: Optional[str] = None


class GraphCreateRequest(BaseModel):
    name: str
    start_node: str
    nodes: List[NodeConfig]
    edges: List[EdgeConfig]


class GraphCreateResponse(BaseModel):
    graph_id: str


class GraphRunRequest(BaseModel):
    graph_id: str
    initial_state: Dict[str, Any] = {}


class StepLog(BaseModel):
    step_index: int
    node_id: str
    tool: str
    state_snapshot: Dict[str, Any]


class GraphRunResponse(BaseModel):
    run_id: str
    final_state: Dict[str, Any]
    log: List[StepLog]
    status: Literal["running", "completed", "failed"]


class RunStateResponse(BaseModel):
    run_id: str
    graph_id: str
    status: Literal["running", "completed", "failed"]
    current_node: Optional[str]
    state: Dict[str, Any]
    log: List[StepLog]
