import os
from pathlib import Path
import unicodedata

from dotenv import load_dotenv
from langchain_core.tools import tool
from openai import OpenAI
from openai import APIConnectionError

load_dotenv()


def normalize_topic(topic: str) -> str:
    normalized = unicodedata.normalize("NFC", topic).strip()
    return " ".join(normalized.split())


def get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    return OpenAI(api_key=api_key)


def call_text_model(*, instructions: str, prompt: str, temperature: float = 0.7) -> str:
    instructions = instructions.strip()
    prompt = prompt.strip()
    if not instructions:
        raise ValueError("Model instructions must not be empty.")
    if not prompt:
        raise ValueError("Model prompt must not be empty.")

    client = get_openai_client()
    model = os.getenv("OPENAI_TEXT_MODEL", "gpt-4.1-mini")
    response = client.responses.create(
        model=model,
        instructions=instructions,
        input=prompt,
        temperature=temperature,
        max_output_tokens=2600,
    )
    return response.output_text.strip()


@tool
def science_fact_tool(topic: str) -> str:
    """Return a simple science fact for a children's audio script."""
    topic = normalize_topic(topic)
    facts = {
        "왜 모기가 물면 간지럽나요": (
            "모기가 피부를 물 때는 작은 침을 함께 넣는데, 우리 몸이 그 침에 반응해서 간지럽게 느껴져요."
        ),
    }
    return facts.get(
        topic.lower(),
        f"{topic}는 어린이 눈높이에서 쉽고 짧게 설명할 수 있는 과학 주제예요.",
    )


@tool
def parent_tip_tool() -> str:
    """Return one simple follow-up tip for parents."""
    return "에피소드가 끝난 뒤 아이에게 가장 기억에 남는 과학 내용을 한 가지 말해보게 해주세요."


def fallback_radio_script(*, topic: str, science_fact: str, duration_minutes: int) -> str:
    normalized_topic = normalize_topic(topic)
    loops = max(1, duration_minutes)
    detail_sections = [
        [
            "[Dr. Spark] 먼저 머릿속으로 장면 하나를 떠올려 보세요. 평범한 일처럼 보여도 그 안에는 늘 이유가 숨어 있답니다.",
            f"[Dr. Spark] {normalized_topic}도 마찬가지예요. 겉으로 보기엔 단순해 보여도, 자세히 보면 몸과 자연이 아주 바쁘게 움직이고 있지요.",
            f"[Dr. Spark] 그래서 가장 중요한 과학 포인트는 이것이에요. {science_fact}",
            "[Dr. Spark] 이렇게 이유를 알고 나면, 그냥 신기한 일이 아니라 이해할 수 있는 일이 된단다.",
        ],
        [
            "[Dr. Spark] 과학은 어려운 말부터 시작하지 않아요. 눈으로 보고, 몸으로 느끼고, 왜 그런지 묻는 데서 시작해요.",
            f"[Dr. Spark] 오늘 주제인 {normalized_topic}도 바로 그런 질문이에요.",
            "[Dr. Spark] 처음에는 '그냥 그런가 보다' 하고 지나칠 수 있지만, 한 번 이유를 듣고 나면 다음부터는 다르게 보일 거예요.",
            f"[Dr. Spark] 다시 쉽게 풀어 말하면, {science_fact}",
        ],
        [
            "[Dr. Spark] 이제 한 걸음 더 들어가 볼까요?",
            "[Dr. Spark] 우리 몸과 자연은 필요할 때마다 스스로 반응하고, 스스로 신호를 보내기도 해요.",
            "[Dr. Spark] 그래서 어떤 느낌이 들거나 어떤 일이 생기면, 그것도 몸이 보내는 작은 이야기일 수 있답니다.",
            f"[Dr. Spark] 오늘 배운 내용도 바로 그런 이야기와 연결돼요. {science_fact}",
        ],
        [
            "[Dr. Spark] 이런 내용을 알고 있으면 다음에 비슷한 일을 만났을 때 덜 당황하게 돼요.",
            "[Dr. Spark] 그리고 '무조건 이상한 일'이라고 생각하기보다, '어떤 원리가 있겠구나' 하고 차분히 생각하게 되지요.",
            f"[Dr. Spark] 과학은 정답을 외우는 일이 아니라, {normalized_topic} 같은 궁금증에 이유를 붙여 보는 연습이란다.",
            "[Dr. Spark] 그래서 작은 질문 하나가 커다란 배움으로 이어질 수 있어요.",
        ],
        [
            "[Dr. Spark] 친구들에게도 오늘 들은 이야기를 들려줄 수 있겠지요.",
            "[Dr. Spark] 내가 이해한 것을 다른 사람에게 설명해 보면, 내 머릿속에서도 더 또렷하게 정리된답니다.",
            f"[Dr. Spark] 오늘의 핵심은 여전히 같아요. {science_fact}",
            "[Dr. Spark] 중요한 건 무섭거나 낯설게 느껴지는 일도 이유를 알면 훨씬 편안해진다는 거예요.",
        ],
    ]
    lines = [
        f"[Dr. Spark] 안녕, 친구들. 오늘은 {normalized_topic}에 대해 함께 알아볼 거예요.",
        "[Dr. Spark] 우리 주변에는 그냥 지나치기엔 아까운 신기한 질문들이 아주 많지요.",
        f"[Dr. Spark] 오늘의 질문은 바로 이것이에요. {normalized_topic}",
        "[Dr. Spark] 이런 질문을 해보는 마음이 바로 과학의 출발점이란다.",
        f"[Dr. Spark] 먼저 가장 중요한 답부터 차근차근 이야기해볼게요. {science_fact}",
        "[Dr. Spark] 그런데 과학은 답 하나만 외우는 공부가 아니에요.",
        "[Dr. Spark] 왜 그런지, 우리 몸이나 자연이 어떻게 움직이는지 함께 상상해보면 훨씬 더 재미있어진답니다.",
    ]

    for step in range(loops):
        lines.extend(detail_sections[step % len(detail_sections)])

    lines.extend(
        [
            "[Dr. Spark] 오늘 들은 내용을 한 문장으로 정리하면, 궁금한 일에도 분명한 까닭이 숨어 있다는 거예요.",
            f"[Dr. Spark] {normalized_topic}에 대해 알게 되니, 평범한 하루가 조금 더 신기하게 보이지 않나요?",
            "[Dr. Spark] 다음에 같은 일을 만나면 잠깐 멈춰서 이유를 떠올려 보세요.",
            "[Dr. Spark] 그렇게 하나씩 이유를 찾다 보면, 여러분도 멋진 과학 탐험가가 될 수 있답니다.",
            "[Dr. Spark] 오늘 과학 라디오는 여기까지예요. 다음 시간에도 재미있는 질문으로 다시 만나요.",
        ]
    )
    return "\n\n".join(lines)


def get_script_length_targets(duration_minutes: int) -> tuple[int, int]:
    minutes = max(1, duration_minutes)
    target_lines = max(12, minutes * 9)
    target_chars = max(700, minutes * 850)
    return target_lines, target_chars


def fallback_parent_summary(*, topic: str, science_fact: str, parent_tip: str) -> str:
    return (
        f"주제: {normalize_topic(topic)}. "
        f"핵심 과학 포인트: {science_fact} "
        f"부모 가이드: {parent_tip} "
        "추천 활용: 아이에게 오늘 가장 신기했던 부분을 한 문장으로 말해보게 해주세요."
    )


def generate_radio_script(*, topic: str, science_fact: str, duration_minutes: int, tone: str) -> str:
    target_lines, target_chars = get_script_length_targets(duration_minutes)
    instructions = """
당신은 어린이 과학 라디오 작가입니다.
반드시 한국어로만 작성하세요.
화자는 오직 [Dr. Spark] 한 명뿐입니다.
설명은 자연스럽고 따뜻해야 하며, 유치원/초등 저학년이 귀로 듣고 이해할 수 있어야 합니다.
나열식 요약문처럼 쓰지 말고, 라디오에서 실제로 들려주는 이야기처럼 써주세요.
문장은 짧고 리듬감 있게 쓰고, 같은 말투인 '...란다', '...이지', '...해요'를 섞어 부드럽게 들리게 하세요.
도입, 궁금증 제시, 쉬운 설명, 의미 정리, 따뜻한 마무리가 모두 들어가야 합니다.
길이 요구를 매우 중요하게 지키세요. 특히 5분 요청이면 짧은 소개문 수준으로 끝내면 안 됩니다.
사용자가 요청한 주제만 다루고, 관련 없는 과학 상식이나 다른 주제로 넓히지 마세요.
주제 수를 늘리거나 새 질문을 추가하지 마세요.
출력은 [Dr. Spark]로 시작하는 여러 줄 대본만 출력하세요.
"""
    prompt = f"""
주제: {normalize_topic(topic)}
길이: 약 {duration_minutes}분
톤: {tone}
반드시 반영할 핵심 사실: {science_fact}
분량 목표:
- 최소 {target_lines}문장 이상
- 최소 {target_chars}자 이상
- {duration_minutes}분 분량에 맞게 설명과 예시를 충분히 풀어서 말할 것

원하는 스타일:
- 아이가 '왜 그럴까?' 하고 귀를 기울이게 만드는 도입
- 설명은 쉽지만 유치하지 않음
- 예시처럼 자연스러운 연결 문장 사용
- 한두 문단 요약처럼 끝내지 말고, 실제 라디오 진행처럼 충분히 이어갈 것
- 핵심 설명을 다른 쉬운 표현으로 한 번 더 풀어주기
- 중간중간 아이가 장면을 떠올릴 수 있는 말 넣기
- 마지막은 다음 시간도 기대하게 하는 라디오 마무리
"""
    try:
        return call_text_model(instructions=instructions, prompt=prompt, temperature=0.8)
    except (RuntimeError, APIConnectionError, Exception):
        return fallback_radio_script(
            topic=topic,
            science_fact=science_fact,
            duration_minutes=duration_minutes,
        )


def revise_radio_script(
    *,
    topic: str,
    script: str,
    science_fact: str,
    revision_request: str,
    tone: str,
) -> str:
    instructions = """
당신은 어린이 과학 라디오 작가입니다.
기존 대본을 부모 요청에 맞게 더 자연스럽게 수정하세요.
반드시 한국어로만 작성하세요.
화자는 [Dr. Spark] 한 명뿐입니다.
기존 대본의 장점은 살리고, 수정 요청만 반영해 더 부드럽게 다듬으세요.
기존 주제 범위를 벗어나 새 내용을 덧붙이지 마세요.
출력은 수정된 최종 대본만 출력하세요.
"""
    prompt = f"""
주제: {normalize_topic(topic)}
톤: {tone}
핵심 사실: {science_fact}
수정 요청: {revision_request}

기존 대본:
{script}
"""
    try:
        return call_text_model(instructions=instructions, prompt=prompt, temperature=0.7)
    except (RuntimeError, APIConnectionError, Exception):
        return (
            f"{script}\n\n"
            f"[Dr. Spark] 부모님이 부탁하신 내용을 반영해서 더 쉽게 다시 정리해볼게요. {revision_request}\n"
            "[Dr. Spark] 방금 들은 내용을 천천히 떠올려 보면 훨씬 더 쉽게 이해할 수 있단다."
        )


def generate_parent_summary(*, topic: str, science_fact: str, parent_tip: str, script: str) -> str:
    instructions = """
당신은 부모용 교육 요약을 작성하는 도우미입니다.
반드시 한국어로만 작성하세요.
출력은 짧은 한 단락으로 쓰세요.
스크립트에 없는 새 정보는 추가하지 마세요.
포함할 내용:
1. 오늘 에피소드의 핵심 과학 개념
2. 부모가 아이와 나눌 수 있는 한 가지 후속 질문 또는 활동
"""
    prompt = f"""
주제: {normalize_topic(topic)}
핵심 사실: {science_fact}
부모 팁: {parent_tip}
대본:
{script}
"""
    try:
        return call_text_model(instructions=instructions, prompt=prompt, temperature=0.4)
    except (RuntimeError, APIConnectionError, Exception):
        return fallback_parent_summary(topic=topic, science_fact=science_fact, parent_tip=parent_tip)


def synthesize_speech_to_wav(
    *,
    text: str,
    voice: str,
    output_path: str,
    instructions: str | None = None,
    model: str = "gpt-4o-mini-tts",
) -> str:
    text = text.strip()
    if not text:
        raise ValueError("TTS input text must not be empty.")

    client = get_openai_client()
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    response = client.audio.speech.create(
        model=model,
        voice=voice,
        input=text,
        instructions=instructions,
        response_format="wav",
    )
    response.write_to_file(path)
    return str(path)
