from .engine import GraphEngine
from .models import NodeConfig, EdgeConfig


def create_summarization_workflow(engine: GraphEngine) -> str:
    """
    Build the 'Summarization + Refinement' workflow.

    Nodes:
      1. split          -> split_text
      2. summarize      -> summarize_chunks
      3. merge          -> merge_summaries
      4. evaluate       -> evaluate_summary
      5. refine         -> refine_summary

    Flow:
      split -> summarize -> merge -> evaluate
      evaluate:
         if summary_length > 80 -> refine
         else -> end
      refine -> evaluate  (loop)
    """

    nodes = [
        NodeConfig(id="split", tool="split_text", config={"chunk_size": 80}),
        NodeConfig(id="summarize", tool="summarize_chunks", config={"per_chunk_summary_size": 30}),
        NodeConfig(id="merge", tool="merge_summaries", config={}),
        NodeConfig(id="evaluate", tool="evaluate_summary", config={}),
        NodeConfig(id="refine", tool="refine_summary", config={"max_summary_words": 80}),
    ]

    edges = [
        # Linear edges
        EdgeConfig(from_node="split", to_node="summarize"),
        EdgeConfig(from_node="summarize", to_node="merge"),
        EdgeConfig(from_node="merge", to_node="evaluate"),

        # Conditional edge: evaluate -> refine / end
        EdgeConfig(
            from_node="evaluate",
            condition_key="summary_length",
            condition_op="gt",
            condition_value=80,
            true_target="refine",
            false_target=None,  # None means terminate
        ),

        # Loop edge: refine -> evaluate
        EdgeConfig(from_node="refine", to_node="evaluate"),
    ]

    graph_id = engine.create_graph(
        name="summarization_and_refinement",
        start_node="split",
        nodes_cfg=nodes,
        edges_cfg=edges,
    )
    return graph_id
