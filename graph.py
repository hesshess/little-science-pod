from langgraph.graph import END, START, StateGraph

from nodes import (
    fetch_parent_tip,
    fetch_science_fact,
    fetch_vocabulary,
    orchestrate_research,
    plan_episode,
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
    graph_builder.add_node("orchestrate_research", orchestrate_research)
    graph_builder.add_node("fetch_science_fact", fetch_science_fact)
    graph_builder.add_node("fetch_vocabulary", fetch_vocabulary)
    graph_builder.add_node("fetch_parent_tip", fetch_parent_tip)
    graph_builder.add_node("write_script", write_script)
    graph_builder.add_node("review_script", review_script)
    graph_builder.add_node("revise_script", revise_script)
    graph_builder.add_node("summarize_for_parent", summarize_for_parent)

    graph_builder.add_edge(START, "plan_episode")
    graph_builder.add_edge("plan_episode", "orchestrate_research")
    graph_builder.add_edge("orchestrate_research", "fetch_science_fact")
    graph_builder.add_edge("orchestrate_research", "fetch_vocabulary")
    graph_builder.add_edge("orchestrate_research", "fetch_parent_tip")
    graph_builder.add_edge("fetch_science_fact", "write_script")
    graph_builder.add_edge("fetch_vocabulary", "write_script")
    graph_builder.add_edge("fetch_parent_tip", "write_script")
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
