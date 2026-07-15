from langgraph.graph import END, START, StateGraph

from nodes import (
    fetch_parent_tip,
    fetch_science_fact,
    orchestrate_research,
    plan_episode,
    review_script,
    revise_script,
    route_after_review,
    route_after_summary,
    split_dialogue,
    summarize_for_parent,
    synthesize_doctor_voice,
    write_script,
)
from state import EpisodeState


def build_graph():
    graph_builder = StateGraph(EpisodeState)
    graph_builder.add_node("plan_episode", plan_episode)
    graph_builder.add_node("orchestrate_research", orchestrate_research)
    graph_builder.add_node("fetch_science_fact", fetch_science_fact)
    graph_builder.add_node("fetch_parent_tip", fetch_parent_tip)
    graph_builder.add_node("write_script", write_script)
    graph_builder.add_node("review_script", review_script)
    graph_builder.add_node("revise_script", revise_script)
    graph_builder.add_node("summarize_for_parent", summarize_for_parent)
    graph_builder.add_node("split_dialogue", split_dialogue)
    graph_builder.add_node("synthesize_doctor_voice", synthesize_doctor_voice)

    graph_builder.add_edge(START, "plan_episode")
    graph_builder.add_edge("plan_episode", "orchestrate_research")
    graph_builder.add_edge("orchestrate_research", "fetch_science_fact")
    graph_builder.add_edge("orchestrate_research", "fetch_parent_tip")
    graph_builder.add_edge("fetch_science_fact", "write_script")
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
    graph_builder.add_conditional_edges(
        "summarize_for_parent",
        route_after_summary,
        {
            "audio": "split_dialogue",
            "done": END,
        },
    )
    graph_builder.add_edge("split_dialogue", "synthesize_doctor_voice")
    graph_builder.add_edge("synthesize_doctor_voice", END)

    return graph_builder.compile()
