from fastapi import FastAPI, HTTPException
from typing import Dict, Any

from .engine import GraphEngine, ToolRegistry
from .models import (
    GraphCreateRequest,
    GraphCreateResponse,
    GraphRunRequest,
    GraphRunResponse,
    RunStateResponse,
)
from .tools import register_default_tools
from .workflows import create_summarization_workflow


app = FastAPI(title="Minimal Agent Workflow Engine")

# Global engine + registry
tool_registry = ToolRegistry()
register_default_tools(tool_registry)

engine = GraphEngine(tool_registry=tool_registry)

# Create example workflow on startup
EXAMPLE_GRAPH_ID: str = create_summarization_workflow(engine)


@app.get("/")
def root() -> Dict[str, Any]:
    return {
        "message": "Minimal agent workflow engine is running.",
        "example_graph_id": EXAMPLE_GRAPH_ID,
        "tools": tool_registry.list_tools(),
    }


# ---------- GRAPH ENDPOINTS ----------


@app.post("/graph/create", response_model=GraphCreateResponse)
def create_graph(request: GraphCreateRequest) -> GraphCreateResponse:
    """
    Create a new graph from JSON description.

    Body example:
    {
      "name": "my_graph",
      "start_node": "n1",
      "nodes": [...],
      "edges": [...]
    }
    """
    graph_id = engine.create_graph(
        name=request.name,
        start_node=request.start_node,
        nodes_cfg=request.nodes,
        edges_cfg=request.edges,
    )
    return GraphCreateResponse(graph_id=graph_id)


@app.post("/graph/run", response_model=GraphRunResponse)
def run_graph(request: GraphRunRequest) -> GraphRunResponse:
    """
    Run a graph end-to-end with the given initial state.

    Body example (for example workflow):
    {
      "graph_id": "<EXAMPLE_GRAPH_ID>",
      "initial_state": {
        "text": "some long text...",
        "chunk_size": 80,
        "per_chunk_summary_size": 30,
        "max_summary_words": 80
      }
    }
    """
    try:
        run = engine.run_graph(
            graph_id=request.graph_id,
            initial_state=request.initial_state,
        )
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return GraphRunResponse(
        run_id=run.id,
        final_state=run.state,
        log=run.log,
        status=run.status,  # "running" / "completed" / "failed"
    )


@app.get("/graph/state/{run_id}", response_model=RunStateResponse)
def get_run_state(run_id: str) -> RunStateResponse:
    """
    Fetch the current state and execution log for a given run.

    In this minimal version, runs are executed synchronously,
    so this will typically return the final state.
    """
    try:
        run = engine.get_run(run_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return RunStateResponse(
        run_id=run.id,
        graph_id=run.graph_id,
        status=run.status,
        current_node=run.current_node,
        state=run.state,
        log=run.log,
    )
