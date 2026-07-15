from state import EpisodeState
from tools import parent_tip_tool, science_fact_tool, vocabulary_tool


def plan_episode(state: EpisodeState) -> EpisodeState:
    plan = (
        f"- Audience: {state['age_group']}\n"
        f"- Topic: {state['topic']}\n"
        f"- Length: about {state['duration_minutes']} minutes\n"
        f"- Tone: {state['tone']}\n"
        "- Characters: Curious Kid Leo, Dr. Spark\n"
        "- Goal: teach one science idea with easy English and repetition"
    )
    return {"plan": plan}


def orchestrate_research(state: EpisodeState) -> EpisodeState:
    return {"plan": f"{state['plan']}\n- Research workflow: fact, vocabulary, and parent tip in parallel"}


def fetch_science_fact(state: EpisodeState) -> EpisodeState:
    science_fact = science_fact_tool.invoke({"topic": state["topic"]})
    return {"science_fact": science_fact}


def fetch_vocabulary(state: EpisodeState) -> EpisodeState:
    target_words = vocabulary_tool.invoke({"topic": state["topic"]})
    return {"target_words": target_words}


def fetch_parent_tip(state: EpisodeState) -> EpisodeState:
    parent_tip = parent_tip_tool.invoke({"age_group": state["age_group"]})
    return {"parent_tip": parent_tip}


def write_script(state: EpisodeState) -> EpisodeState:
    topic = state["topic"]
    fact = state["science_fact"]
    words = ", ".join(state["target_words"])
    script = f"""
[Leo] Dr. Spark, I want to learn about {topic}!

[Dr. Spark] Great question, Leo. Here is a simple idea: {fact}

[Leo] Wow! Can you say it again?

[Dr. Spark] Sure. Learning about {topic} is fun. Look up! Ask why! Science is fun!

[Leo] Look up! Ask why! Science is fun!

[Dr. Spark] Today's words are: {words}.
""".strip()
    return {"script": script}


def review_script(state: EpisodeState) -> EpisodeState:
    return {"review_status": state.get("review_status", "approve")}


def route_after_review(state: EpisodeState) -> str:
    return state["review_status"]


def revise_script(state: EpisodeState) -> EpisodeState:
    revision_request = state.get(
        "revision_request",
        "Make the explanation even simpler for young children.",
    )
    revised_script = (
        f"{state['script']}\n\n"
        f"[Dr. Spark] Parent request noted: {revision_request}\n"
        "[Dr. Spark] Let me say it in an even easier way. Science can be simple and fun!"
    )
    return {"script": revised_script, "review_status": "approve"}


def summarize_for_parent(state: EpisodeState) -> EpisodeState:
    summary = (
        f"Topic: {state['topic']}. "
        f"Core fact: {state['science_fact']} "
        f"Target words: {', '.join(state['target_words'])}. "
        f"Parent tip: {state['parent_tip']} "
        "Repeated expressions: 'Look up!', 'Ask why!', 'Science is fun!'"
    )
    return {"parent_summary": summary}
