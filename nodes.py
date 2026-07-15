from pathlib import Path
import re

from state import EpisodeState
from tools import (
    generate_parent_summary,
    generate_radio_script,
    normalize_topic,
    parent_tip_tool,
    revise_radio_script,
    science_fact_tool,
    synthesize_speech_to_wav,
)


def topic_slug(topic: str) -> str:
    normalized = normalize_topic(topic).lower().replace(" ", "_")
    slug = re.sub(r"[^0-9a-zA-Z_가-힣]", "", normalized)
    return slug or "episode"


def plan_episode(state: EpisodeState) -> EpisodeState:
    plan = (
        f"- Topic: {state['topic']}\n"
        f"- Length: about {state['duration_minutes']} minutes\n"
        f"- Tone: {state['tone']}\n"
        "- Speaker: Dr. Spark\n"
        "- Goal: explain one science idea in Korean in a warm radio style"
    )
    return {"plan": plan}


def orchestrate_research(state: EpisodeState) -> EpisodeState:
    return {"plan": f"{state['plan']}\n- Research workflow: fact and parent tip in parallel"}


def fetch_science_fact(state: EpisodeState) -> EpisodeState:
    science_fact = science_fact_tool.invoke({"topic": normalize_topic(state["topic"])})
    return {"science_fact": science_fact}


def fetch_parent_tip(state: EpisodeState) -> EpisodeState:
    parent_tip = parent_tip_tool.invoke({})
    return {"parent_tip": parent_tip}


def write_script(state: EpisodeState) -> EpisodeState:
    script = generate_radio_script(
        topic=state["topic"],
        science_fact=state["science_fact"],
        duration_minutes=state["duration_minutes"],
        tone=state["tone"],
    )
    return {"script": script}


def review_script(state: EpisodeState) -> EpisodeState:
    return {"review_status": state.get("review_status", "approve")}


def route_after_review(state: EpisodeState) -> str:
    return state["review_status"]


def revise_script(state: EpisodeState) -> EpisodeState:
    revision_request = state.get(
        "revision_request",
        "설명을 조금 더 쉽고 자연스럽게 다듬어주세요.",
    )
    revised_script = revise_radio_script(
        topic=state["topic"],
        script=state["script"],
        science_fact=state["science_fact"],
        revision_request=revision_request,
        tone=state["tone"],
    )
    return {"script": revised_script, "review_status": "approve"}


def summarize_for_parent(state: EpisodeState) -> EpisodeState:
    summary = generate_parent_summary(
        topic=state["topic"],
        science_fact=state["science_fact"],
        parent_tip=state["parent_tip"],
        script=state["script"],
    )
    return {"parent_summary": summary}


def route_after_summary(state: EpisodeState) -> str:
    return "audio" if state.get("generate_audio", False) else "done"


def split_dialogue(state: EpisodeState) -> EpisodeState:
    doctor_lines: list[str] = []

    for raw_line in state["script"].splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("[Dr. Spark]"):
            spoken_line = line.replace("[Dr. Spark]", "", 1).strip()
            if spoken_line:
                doctor_lines.append(spoken_line)

    if not doctor_lines:
        fallback_text = state.get("script", "").replace("[Dr. Spark]", "").strip()
        if fallback_text:
            doctor_lines = [fallback_text]

    return {"doctor_lines": doctor_lines}


def synthesize_doctor_voice(state: EpisodeState) -> EpisodeState:
    output_dir = Path(state.get("output_dir", "outputs"))
    output_path = output_dir / f"{topic_slug(state['topic'])}_episode.wav"
    doctor_text = "\n".join(line.strip() for line in state.get("doctor_lines", []) if line.strip()).strip()
    if not doctor_text:
        raise ValueError("TTS용 대본이 비어 있습니다. 스크립트 생성 결과를 확인해주세요.")
    doctor_audio_path = synthesize_speech_to_wav(
        text=doctor_text,
        voice="sage",
        output_path=str(output_path),
        instructions="Speak in Korean like a warm children's science radio host.",
    )
    return {"doctor_audio_path": doctor_audio_path, "final_audio_path": doctor_audio_path}
