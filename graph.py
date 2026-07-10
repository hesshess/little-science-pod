from langgraph.graph import END, START, StateGraph

from nodes import (
    plan_episode,
    research_topic,
    review_script,
    revise_script,
    route_after_review,
    summarize_for_parent,
    write_script,
)
from state import EpisodeState


def build_graph():
    graph_builder = StateGraph(EpisodeState)
    graph_builder.add_node("plan_episode", plan_episode)
    graph_builder.add_node("research_topic", research_topic)
    graph_builder.add_node("write_script", write_script)
    graph_builder.add_node("review_script", review_script)
    graph_builder.add_node("revise_script", revise_script)
    graph_builder.add_node("summarize_for_parent", summarize_for_parent)

    graph_builder.add_edge(START, "plan_episode")
    graph_builder.add_edge("plan_episode", "research_topic")
    graph_builder.add_edge("research_topic", "write_script")
    graph_builder.add_edge("write_script", "review_script")
    graph_builder.add_conditional_edges(
        "review_script",
        route_after_review,
        {
            "approve": "summarize_for_parent",
            "revise": "revise_script",
        },
    )
    graph_builder.add_edge("revise_script", "summarize_for_parent")
    graph_builder.add_edge("summarize_for_parent", END)

    return graph_builder.compile()
