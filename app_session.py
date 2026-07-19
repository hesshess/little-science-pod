import unicodedata

import streamlit as st


def normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFC", text).strip()
    return " ".join(normalized.split())


def is_yes(text: str) -> bool:
    return text.strip().lower() in {"y", "yes", "네", "예"}


def add_assistant_message(content: str) -> None:
    st.session_state.messages.append({"role": "assistant", "content": content})


def clear_error() -> None:
    st.session_state.error_message = None


def set_error(message: str) -> None:
    st.session_state.error_message = message


def reset_chat() -> None:
    st.session_state.messages = []
    st.session_state.stage = "ask_topic"
    st.session_state.pending_topic = None
    st.session_state.topic = None
    st.session_state.duration_minutes = None
    st.session_state.base_request = None
    st.session_state.revision_request = None
    st.session_state.result = None
    st.session_state.error_message = None
    add_assistant_message("안녕하세요. 오늘은 어떤 과학 질문을 라디오로 들어볼까요?")


def ensure_session() -> None:
    if "messages" not in st.session_state:
        reset_chat()


def build_base_request() -> dict:
    return {
        "topic": st.session_state.topic,
        "duration_minutes": st.session_state.duration_minutes,
        "tone": "어린이교육방송톤",
        "generate_audio": False,
        "output_dir": "outputs",
        "review_status": "approve",
    }
