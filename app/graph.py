"""Main Blog Writer LangGraph.

Main flow:
    START
      |
    router
      |
      +---- no research ----> orchestrator
      |
      +---- research -------> orchestrator
                               |
                            fanout
                               |
                         +-----+-----+
                         | worker(s) |
                         +-----+-----+
                               |
                        reducer subgraph
                               |
                              END

Reducer subgraph:
    merge_content -> decide_images -> generate_and_place_images
"""

from langgraph.graph import StateGraph, START, END

from .state import State
from .nodes.router import router_node, route_next
from .nodes.research import research_node
from .nodes.orchestrator import orchestrator_node, fanout
from .nodes.worker import worker_node
from .reducer.graph import reducer_subgraph


def build_graph():
    """Build and compile the complete blog-writing graph."""
    graph = StateGraph(State)

    graph.add_node("router", router_node)
    graph.add_node("research", research_node)
    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("worker", worker_node)
    graph.add_node("reducer", reducer_subgraph)

    graph.add_edge(START, "router")

    graph.add_conditional_edges(
        "router",
        route_next,
        {
            "research": "research",
            "orchestrator": "orchestrator",
        },
    )

    graph.add_edge("research", "orchestrator")

    graph.add_conditional_edges(
        "orchestrator",
        fanout,
        ["worker"],
    )

    graph.add_edge("worker", "reducer")
    graph.add_edge("reducer", END)

    return graph.compile()


app = build_graph()
