import os
import unicodedata
from pathlib import Path

import streamlit as st

from guardrails import parse_duration_minutes, topic_guardrail_message
from graph import build_graph


EXAMPLE_TOPICS = [
    "눈물은 왜 짤까요?",
    "왜 똥을 누어야 할까요?",
    "모기는 왜 사람을 물까요?",
    "충치는 왜 생길까요?",
    "타조는 공룡의 후손일까요?",
]


def normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFC", text).strip()
    return " ".join(normalized.split())


def is_yes(text: str) -> bool:
    return text.strip().lower() in {"y", "yes", "네", "예"}


@st.cache_resource
def get_graph():
    return build_graph()


def add_assistant_message(content: str) -> None:
    st.session_state.messages.append({"role": "assistant", "content": content})


def reset_chat() -> None:
    st.session_state.messages = []
    st.session_state.stage = "ask_topic"
    st.session_state.topic = None
    st.session_state.duration_minutes = None
    st.session_state.base_request = None
    st.session_state.revision_request = None
    st.session_state.result = None
    add_assistant_message("안녕하세요. 주제를 알려주세요. 예: `왜 모기가 물면 간지럽나요`")


def ensure_session() -> None:
    if "messages" not in st.session_state:
        reset_chat()


def get_stage_label(stage: str) -> str:
    labels = {
        "ask_topic": "주제 입력 대기",
        "ask_duration": "길이 입력 대기",
        "ask_revision": "완성본 검토 중",
        "ask_revision_detail": "수정 요청 입력 대기",
        "ask_audio": "오디오 생성 여부 선택",
        "done": "완료",
    }
    return labels.get(stage, "진행 중")


def build_base_request() -> dict:
    return {
        "topic": st.session_state.topic,
        "duration_minutes": st.session_state.duration_minutes,
        "tone": "어린이교육방송톤",
        "generate_audio": False,
        "output_dir": "outputs",
        "review_status": "approve",
    }


def generate_draft() -> None:
    graph = get_graph()
    st.session_state.base_request = build_base_request()
    with st.spinner("완성본 스크립트를 만드는 중이에요..."):
        result = graph.invoke(st.session_state.base_request)
    st.session_state.result = result
    add_assistant_message("완성본 스크립트를 만들었어요.")
    add_assistant_message(f"### 완성본 스크립트\n\n{result['script']}")
    add_assistant_message(f"### 부모용 요약\n\n{result['parent_summary']}")
    add_assistant_message("이 완성본을 수정할까요? `네` 또는 `아니요`로 답해주세요.")
    st.session_state.stage = "ask_revision"


def generate_revision(revision_request: str) -> None:
    graph = get_graph()
    request = {
        **st.session_state.base_request,
        "review_status": "revise",
        "revision_request": revision_request,
    }
    with st.spinner("수정 요청을 반영해서 다시 다듬는 중이에요..."):
        result = graph.invoke(request)
    st.session_state.revision_request = revision_request
    st.session_state.result = result
    add_assistant_message("수정 반영본을 만들었어요.")
    add_assistant_message(f"### 수정된 스크립트\n\n{result['script']}")
    add_assistant_message(f"### 수정 후 부모용 요약\n\n{result['parent_summary']}")
    add_assistant_message("오디오도 생성할까요? `네` 또는 `아니요`로 답해주세요.")
    st.session_state.stage = "ask_audio"


def generate_audio() -> None:
    tts_available = bool(os.getenv("OPENAI_API_KEY")) and os.getenv("ENABLE_TTS") == "1"
    if not tts_available:
        add_assistant_message("오디오 생성은 현재 비활성화되어 있어요. `.env`에 `OPENAI_API_KEY`와 `ENABLE_TTS=1`을 설정해주세요.")
        st.session_state.stage = "done"
        return

    graph = get_graph()
    request = {
        **st.session_state.base_request,
        "generate_audio": True,
        "review_status": "revise" if st.session_state.revision_request else "approve",
    }
    if st.session_state.revision_request:
        request["revision_request"] = st.session_state.revision_request

    with st.spinner("박사님 목소리 오디오를 만드는 중이에요..."):
        result = graph.invoke(request)
    st.session_state.result = result
    audio_path = result.get("final_audio_path")
    if audio_path:
        add_assistant_message(f"오디오 생성이 끝났어요. 파일 경로: `{audio_path}`")
    else:
        add_assistant_message("오디오 생성이 완료되지 않았어요.")
    st.session_state.stage = "done"


st.set_page_config(page_title="리틀사이언스팟", page_icon="🎙️", layout="centered")
ensure_session()

st.title("리틀사이언스팟")
st.caption("어린이 과학 라디오를 만드는 오디오 에이전트")

with st.sidebar:
    
    if st.button("대화 초기화"):
        reset_chat()
        st.rerun()
    tts_enabled = bool(os.getenv("OPENAI_API_KEY")) and os.getenv("ENABLE_TTS") == "1"
    stage_label = get_stage_label(st.session_state.stage)
    current_topic = st.session_state.topic or "아직 없음"
    current_duration = (
        f"{st.session_state.duration_minutes}분"
        if st.session_state.duration_minutes
        else "아직 없음"
    )

    st.markdown("### 현재 진행")
    st.caption(f"단계: {stage_label}")
    st.caption(f"주제: {current_topic}")
    st.caption(f"길이: {current_duration}")

    if st.session_state.result:
        result = st.session_state.result
        st.markdown("### 최근 결과")
        st.write(f"스크립트 길이: 약 {len(result.get('script', ''))}자")
        st.write(f"부모 요약 생성: {'예' if bool(result.get('parent_summary')) else '아니요'}")
        st.write(f"오디오 생성: {'예' if bool(result.get('final_audio_path')) else '아니요'}")

    st.markdown("### 추천 주제")
    for topic in EXAMPLE_TOPICS:
        st.caption(f"- {topic}")

    st.markdown("### 사용 순서")
    st.caption("1. 주제를 입력해요")
    st.caption("2. 원하는 길이를 입력해요")
    st.caption("3. 스크립트를 보고 수정 여부를 정해요")
    st.caption("4. 원하면 오디오까지 만들어요")



for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

result = st.session_state.get("result")
audio_path = result.get("final_audio_path") if result else None
if audio_path and Path(audio_path).exists():
    st.audio(audio_path)

user_input = st.chat_input("메시지를 입력하세요")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    if st.session_state.stage == "ask_topic":
        candidate_topic = normalize_text(user_input)
        guardrail_message = topic_guardrail_message(candidate_topic)
        if guardrail_message:
            add_assistant_message(guardrail_message)
            st.rerun()
        st.session_state.topic = candidate_topic
        add_assistant_message("좋아요. 몇 분짜리로 만들까요? 숫자로 입력해주세요. 예: `1`, `3`")
        st.session_state.stage = "ask_duration"

    elif st.session_state.stage == "ask_duration":
        duration_minutes, duration_message = parse_duration_minutes(normalize_text(user_input))
        if duration_minutes is None:
            add_assistant_message(duration_message or "길이는 숫자로 입력해주세요. 예: `1`, `3`, `5`")
            st.rerun()
        st.session_state.duration_minutes = duration_minutes
        if duration_message:
            add_assistant_message(duration_message)
        generate_draft()

    elif st.session_state.stage == "ask_revision":
        if is_yes(user_input):
            add_assistant_message("어떤 점을 수정할지 알려주세요. 예: `한국어 설명을 더 짧게 해주세요.`")
            st.session_state.stage = "ask_revision_detail"
        else:
            add_assistant_message("좋아요. 오디오도 생성할까요? `네` 또는 `아니요`로 답해주세요.")
            st.session_state.stage = "ask_audio"

    elif st.session_state.stage == "ask_revision_detail":
        generate_revision(normalize_text(user_input))

    elif st.session_state.stage == "ask_audio":
        if is_yes(user_input):
            generate_audio()
        else:
            add_assistant_message("좋아요. 이번에는 텍스트 결과만 마무리할게요.")
            st.session_state.stage = "done"

    elif st.session_state.stage == "done":
        add_assistant_message("새 에피소드를 만들려면 왼쪽의 `대화 초기화` 버튼을 눌러주세요.")

    st.rerun()
