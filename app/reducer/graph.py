"""ReducerWithImages LangGraph subgraph."""

from langgraph.graph import StateGraph, START, END

from ..state import State
from .nodes import (
    merge_content,
    decide_images,
    generate_and_place_images,
)


def build_reducer_graph():
    """Build and compile the reducer/image subgraph."""
    reducer_graph = StateGraph(State)

    reducer_graph.add_node("merge_content", merge_content)
    reducer_graph.add_node("decide_images", decide_images)
    reducer_graph.add_node(
        "generate_and_place_images",
        generate_and_place_images,
    )

    reducer_graph.add_edge(START, "merge_content")
    reducer_graph.add_edge("merge_content", "decide_images")
    reducer_graph.add_edge("decide_images", "generate_and_place_images")
    reducer_graph.add_edge("generate_and_place_images", END)

    return reducer_graph.compile()


reducer_subgraph = build_reducer_graph()
