import os

import streamlit as st


EXAMPLE_TOPICS = [
    "모기는 왜 사람을 물까요?",
    "눈물은 왜 짤까요?",
    "충치는 왜 생길까요?",
]


def inject_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --sea-deep: #0f4c81;
            --sea-mid: #1f7bb6;
            --sea-light: #87d7ff;
            --foam: #f4fbff;
            --sand: #fff4d6;
            --coral: #ff8e6e;
            --ink: #11324d;
        }

        .stApp {
            background:
                radial-gradient(circle at 15% 20%, rgba(135, 215, 255, 0.55), transparent 22%),
                radial-gradient(circle at 85% 10%, rgba(255, 244, 214, 0.5), transparent 20%),
                linear-gradient(180deg, #d9f4ff 0%, #95d8f5 34%, #5bb6df 66%, #2a7bac 100%);
            color: var(--ink);
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(10, 63, 110, 0.96) 0%, rgba(23, 104, 156, 0.94) 100%);
            border-right: 1px solid rgba(255, 255, 255, 0.12);
        }

        [data-testid="stSidebar"] * {
            color: #f5fcff;
        }

        .block-container {
            padding-top: 1.6rem;
            padding-bottom: 3rem;
        }

        h1, h2, h3 {
            font-family: "Marker Felt", "Apple SD Gothic Neo", "Trebuchet MS", sans-serif;
        }

        .hero-shell {
            background: linear-gradient(135deg, rgba(255,255,255,0.92), rgba(234,249,255,0.97));
            border: 1px solid rgba(17, 50, 77, 0.08);
            border-radius: 28px;
            padding: 1.4rem 1.5rem;
            box-shadow: 0 18px 50px rgba(17, 50, 77, 0.14);
            margin-bottom: 1rem;
        }

        .hero-title {
            font-size: 2.4rem;
            line-height: 1.05;
            margin: 0 0 0.5rem 0;
            color: var(--ink);
        }

        .hero-subtitle {
            margin: 0;
            color: #24506e;
        }

        .sidebar-card {
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.14);
            border-radius: 18px;
            padding: 0.9rem 1rem;
            margin-bottom: 0.8rem;
        }

        [data-testid="stChatMessage"] {
            background: rgba(255, 255, 255, 0.78);
            border: 1px solid rgba(17, 50, 77, 0.08);
            border-radius: 20px;
            box-shadow: 0 8px 24px rgba(17, 50, 77, 0.08);
            padding-right: 0.75rem;
        }

        [data-testid="stChatMessage"] * {
            color: #11324d !important;
        }

        [data-testid="stChatMessageContent"] {
            padding: 0.25rem 1.1rem 0.25rem 0.35rem;
        }

        [data-testid="stChatMessage"] code {
            background: rgba(255, 255, 255, 0.95) !important;
            color: #0f4c81 !important;
            border: 1px solid rgba(17, 50, 77, 0.12);
            border-radius: 10px;
            padding: 0.1rem 0.38rem;
        }

        [data-testid="stChatInput"] {
            background: rgba(255, 255, 255, 0.96) !important;
            border: 1px solid rgba(17, 50, 77, 0.12);
            border-radius: 18px;
            box-shadow: 0 8px 20px rgba(17, 50, 77, 0.08);
        }

        [data-testid="stChatInput"] > div,
        [data-testid="stChatInput"] > div > div {
            background: rgba(255, 255, 255, 0.96) !important;
            border-radius: 18px;
        }

        [data-testid="stChatInput"] textarea,
        [data-testid="stChatInput"] input {
            color: #11324d !important;
            -webkit-text-fill-color: #11324d !important;
            caret-color: #11324d !important;
            background: rgba(255, 255, 255, 0.96) !important;
        }

        [data-testid="stChatInput"] textarea::placeholder,
        [data-testid="stChatInput"] input::placeholder {
            color: rgba(17, 50, 77, 0.58) !important;
            -webkit-text-fill-color: rgba(17, 50, 77, 0.58) !important;
        }

        .stButton > button {
            background: linear-gradient(135deg, #ff9b77, #ffb85b);
            color: #18344f;
            border: none;
            border-radius: 999px;
            font-weight: 700;
        }

        .stAudio {
            background: rgba(255,255,255,0.8);
            border-radius: 18px;
            padding: 0.5rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero-shell">
            <h1 class="hero-title">리틀사이언스팟</h1>
            <p class="hero-subtitle">과학 질문 하나를 짧은 어린이 라디오와 오디오로 바꿔드려요.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(*, topic: str | None, duration_minutes: int | None) -> bool:
    current_topic = topic or "아직 없음"
    current_duration = f"{duration_minutes}분" if duration_minutes else "아직 없음"
    tts_enabled = bool(os.getenv("OPENAI_API_KEY")) and os.getenv("ENABLE_TTS") == "1"

    with st.sidebar:
        st.markdown(
            f"""
            <div class="sidebar-card">
                <h3>현재 상태</h3>
                <div>주제: {current_topic}</div>
                <div>길이: {current_duration}</div>
                <div>오디오: {'가능' if tts_enabled else '준비 필요'}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### 예시 질문")
        for topic_name in EXAMPLE_TOPICS:
            st.caption(f"- {topic_name}")

        st.markdown("### 사용 순서")
        st.caption("1. 과학 질문 입력")
        st.caption("2. 주제 확인")
        st.caption("3. 길이 입력")
        st.caption("4. 완성본 확인 후 수정")
        st.caption("5. 원하면 오디오 생성")

        return st.button("새로 시작하기")
