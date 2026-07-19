import os
import re
from pathlib import Path

import streamlit as st

from app_session import add_assistant_message, build_base_request, clear_error, set_error
from graph import build_graph
from tools import normalize_topic, synthesize_speech_to_wav


@st.cache_resource
def get_graph():
    return build_graph()


def topic_slug(topic: str) -> str:
    normalized = normalize_topic(topic).lower().replace(" ", "_")
    slug = re.sub(r"[^0-9a-zA-Z_가-힣]", "", normalized)
    return slug or "episode"


def explain_error(error: Exception, *, context: str) -> str:
    raw = str(error).strip()
    if "OPENAI_API_KEY" in raw:
        return f"{context} 중 API 설정을 찾지 못했어요. Streamlit Cloud에서는 `OPENAI_API_KEY`를 Secrets에 넣어주세요."
    if "TTS input text must not be empty" in raw or "TTS용 대본이 비어 있습니다" in raw:
        return "오디오로 바꿀 대본이 비어 있어요. 스크립트를 다시 생성한 뒤 다시 시도해주세요."
    if raw:
        return f"{context} 중 문제가 생겼어요: {raw}"
    return f"{context} 중 문제가 생겼어요. 잠시 후 다시 시도해주세요."


def run_graph_request(request: dict, *, spinner_text: str, context: str) -> dict | None:
    try:
        with st.spinner(spinner_text):
            result = get_graph().invoke(request)
    except Exception as error:
        message = explain_error(error, context=context)
        set_error(message)
        add_assistant_message(message)
        return None

    clear_error()
    return result


def script_to_tts_text(script: str) -> str:
    lines: list[str] = []
    for raw_line in script.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("[Dr. Spark]"):
            line = line.replace("[Dr. Spark]", "", 1).strip()
        if line:
            lines.append(line)
    return "\n".join(lines).strip()


def generate_script() -> None:
    st.session_state.base_request = build_base_request()
    result = run_graph_request(
        st.session_state.base_request,
        spinner_text="돌고래 방송국에서 완성본 스크립트를 만드는 중이에요...",
        context="스크립트 생성",
    )
    if not result:
        return

    st.session_state.result = result
    add_assistant_message("완성본 스크립트를 만들었어요.")
    add_assistant_message(f"### 완성본 스크립트\n\n{result['script']}")
    add_assistant_message(f"### 부모용 요약\n\n{result['parent_summary']}")
    add_assistant_message("이 완성본을 수정할까요? `네` 또는 `아니요`로 답해주세요.")
    st.session_state.stage = "ask_revision"


def generate_revision(revision_request: str) -> None:
    request = {
        **st.session_state.base_request,
        "review_status": "revise",
        "revision_request": revision_request,
    }
    result = run_graph_request(
        request,
        spinner_text="수정 요청을 반영해서 다시 다듬는 중이에요...",
        context="스크립트 수정",
    )
    if not result:
        return

    st.session_state.revision_request = revision_request
    st.session_state.result = result
    add_assistant_message("수정된 완성본을 만들었어요.")
    add_assistant_message(f"### 수정된 스크립트\n\n{result['script']}")
    add_assistant_message(f"### 수정 후 부모용 요약\n\n{result['parent_summary']}")
    add_assistant_message("오디오도 생성할까요? `네` 또는 `아니요`로 답해주세요.")
    st.session_state.stage = "ask_audio"


def generate_audio() -> None:
    if not (os.getenv("OPENAI_API_KEY") and os.getenv("ENABLE_TTS") == "1"):
        message = "오디오 생성은 아직 준비되지 않았어요. Streamlit Cloud Secrets에 `OPENAI_API_KEY`를 넣고 `ENABLE_TTS=1`로 설정해주세요."
        set_error(message)
        add_assistant_message(message)
        st.session_state.stage = "done"
        return

    current_result = st.session_state.result or {}
    current_script = current_result.get("script", "").strip()
    if not current_script:
        message = "먼저 스크립트를 완성한 뒤 오디오를 생성해주세요."
        set_error(message)
        add_assistant_message(message)
        st.session_state.stage = "done"
        return

    tts_text = script_to_tts_text(current_script)
    if not tts_text:
        message = "오디오로 읽을 스크립트가 비어 있어요. 스크립트를 다시 생성해주세요."
        set_error(message)
        add_assistant_message(message)
        st.session_state.stage = "done"
        return

    try:
        with st.spinner("지금 보고 있는 완성본 그대로 오디오를 만드는 중이에요..."):
            output_dir = Path(current_result.get("output_dir", "outputs"))
            output_path = output_dir / f"{topic_slug(st.session_state.topic or 'episode')}_episode.wav"
            audio_path = synthesize_speech_to_wav(
                text=tts_text,
                voice="sage",
                output_path=str(output_path),
                instructions="Speak in Korean like a warm children's science radio host.",
            )
    except Exception as error:
        message = explain_error(error, context="오디오 생성")
        set_error(message)
        add_assistant_message(message)
        return

    clear_error()
    st.session_state.result = {
        **current_result,
        "doctor_audio_path": audio_path,
        "final_audio_path": audio_path,
    }
    add_assistant_message("지금 보고 있는 완성본 스크립트 그대로 오디오를 만들었어요.")
    st.session_state.stage = "done"
