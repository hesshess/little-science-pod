from langchain_core.tools import tool


@tool
def science_fact_tool(topic: str) -> str:
    """Return a simple science fact for a children's audio script."""
    facts = {
        "the moon": (
            "The moon does not make its own light. It reflects light from the sun, "
            "and it moves around Earth."
        ),
        "rainbows": (
            "A rainbow appears when sunlight passes through tiny drops of water and "
            "the light spreads into many colors."
        ),
        "dinosaurs": (
            "Dinosaurs lived a long time ago, and scientists learn about them by "
            "studying fossils in rocks."
        ),
    }
    return facts.get(
        topic.lower(),
        f"{topic.title()} is a science topic we can explain with one simple fact and repeated English phrases.",
    )


@tool
def vocabulary_tool(topic: str) -> list[str]:
    """Return simple English vocabulary words related to the topic."""
    words = {
        "the moon": ["moon", "light", "night"],
        "rainbows": ["rainbow", "color", "rain"],
        "dinosaurs": ["dinosaur", "bone", "fossil"],
    }
    return words.get(topic.lower(), ["science", "learn", "fun"])


@tool
def parent_tip_tool(age_group: str) -> str:
    """Return a parent coaching tip matched to the child's age group."""
    tips = {
        "4-5": "Pause after each short line and let the child repeat one keyword.",
        "6-8": "Ask the child to repeat the key phrase and explain one idea in their own words.",
        "9-10": "Ask one follow-up why-question after the episode to deepen understanding.",
    }
    return tips.get(age_group, "Repeat one key phrase together after listening.")
