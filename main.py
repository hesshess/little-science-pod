from pathlib import Path

import streamlit as st

from app_actions import generate_audio, generate_revision, generate_script
from app_session import (
    add_assistant_message,
    clear_error,
    ensure_session,
    is_yes,
    normalize_text,
    reset_chat,
    set_error,
)
from app_ui import inject_theme, render_hero, render_sidebar
from guardrails import parse_duration_minutes, topic_guardrail_message


def handle_topic_input(user_input: str) -> None:
    candidate_topic = normalize_text(user_input)
    guardrail_message = topic_guardrail_message(candidate_topic)
    if guardrail_message:
        set_error(guardrail_message)
        add_assistant_message(guardrail_message)
        return

    clear_error()
    st.session_state.pending_topic = candidate_topic
    add_assistant_message(
        f"좋아요. 주제를 `{candidate_topic}`로 이해했어요. 이 주제가 맞나요? `네` 또는 `아니요`로 답해주세요."
    )
    st.session_state.stage = "ask_topic_confirm"


def handle_topic_confirmation(user_input: str) -> None:
    if is_yes(user_input):
        st.session_state.topic = st.session_state.pending_topic
        add_assistant_message("좋아요. 몇 분짜리로 만들까요? 숫자로 입력해주세요. 예: `1`, `3`, `5`")
        st.session_state.stage = "ask_duration"
        return

    st.session_state.pending_topic = None
    st.session_state.topic = None
    add_assistant_message("좋아요. 다시 과학 질문을 입력해주세요.")
    st.session_state.stage = "ask_topic"


def handle_duration_input(user_input: str) -> None:
    duration_minutes, duration_message = parse_duration_minutes(normalize_text(user_input))
    if duration_minutes is None:
        set_error(duration_message or "길이는 숫자로 입력해주세요.")
        add_assistant_message(duration_message or "길이는 숫자로 입력해주세요.")
        return

    st.session_state.duration_minutes = duration_minutes
    if duration_message:
        add_assistant_message(duration_message)
    generate_script()


def handle_revision_choice(user_input: str) -> None:
    if is_yes(user_input):
        add_assistant_message("어떤 점을 수정할지 알려주세요. 예: `설명을 조금 더 짧게 해주세요.`")
        st.session_state.stage = "ask_revision_detail"
        return

    add_assistant_message("좋아요. 오디오도 생성할까요? `네` 또는 `아니요`로 답해주세요.")
    st.session_state.stage = "ask_audio"


def handle_audio_choice(user_input: str) -> None:
    if is_yes(user_input):
        generate_audio()
        return

    add_assistant_message("좋아요. 이번에는 텍스트 결과만 마무리할게요.")
    st.session_state.stage = "done"


def handle_user_input(user_input: str) -> None:
    st.session_state.messages.append({"role": "user", "content": user_input})

    if st.session_state.stage == "ask_topic":
        handle_topic_input(user_input)
    elif st.session_state.stage == "ask_topic_confirm":
        handle_topic_confirmation(user_input)
    elif st.session_state.stage == "ask_duration":
        handle_duration_input(user_input)
    elif st.session_state.stage == "ask_revision":
        handle_revision_choice(user_input)
    elif st.session_state.stage == "ask_revision_detail":
        generate_revision(normalize_text(user_input))
    elif st.session_state.stage == "ask_audio":
        handle_audio_choice(user_input)
    elif st.session_state.stage == "done":
        add_assistant_message("새 에피소드를 만들려면 왼쪽의 `새로 시작하기` 버튼을 눌러주세요.")


st.set_page_config(page_title="리틀사이언스팟", page_icon="🐬", layout="centered")
ensure_session()
inject_theme()

if render_sidebar(
    topic=st.session_state.topic,
    duration_minutes=st.session_state.duration_minutes,
):
    reset_chat()
    st.rerun()

render_hero()

if st.session_state.error_message:
    st.error(st.session_state.error_message)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

result = st.session_state.get("result")
audio_path = result.get("final_audio_path") if result else None
if audio_path and Path(audio_path).exists():
    st.audio(audio_path)

user_input = st.chat_input("과학 질문이나 답변을 입력하세요")
if user_input:
    handle_user_input(user_input)
    st.rerun()
