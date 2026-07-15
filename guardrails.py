import re


MAX_DURATION_MINUTES = 5
MIN_DURATION_MINUTES = 1

TOO_BROAD_TOPICS = {
    "과학",
    "우주",
    "동물",
    "공룡",
    "자연",
    "인체",
    "바다",
    "곤충",
    "날씨",
    "지구",
}


def normalize_user_text(text: str) -> str:
    return " ".join(text.strip().split())


def topic_guardrail_message(topic: str) -> str | None:
    normalized = normalize_user_text(topic)
    if not normalized:
        return "주제가 비어 있어요. `모기는 왜 사람을 물까요?`처럼 한 가지 질문으로 입력해주세요."

    if len(normalized) > 80:
        return "주제가 너무 길어요. 한 에피소드에는 질문 하나만 넣어주세요."

    if normalized in TOO_BROAD_TOPICS:
        return f"`{normalized}`는 범위가 너무 넓어요. 한 번에 한 가지 질문으로 좁혀주세요. 예: `모기는 왜 사람을 물까요?`"

    if any(separator in normalized for separator in [",", "/", "&", " 그리고 ", " 및 "]):
        return "한 번에 여러 주제를 넣기보다, 한 에피소드에는 질문 하나만 넣어주세요."

    if re.search(r"\b(여러 가지|아무거나|추천|아무 주제|과학 전반)\b", normalized):
        return "주제가 너무 넓거나 열려 있어요. 듣고 싶은 과학 질문 한 가지만 적어주세요."

    return None


def parse_duration_minutes(raw_text: str) -> tuple[int | None, str | None]:
    normalized = normalize_user_text(raw_text)
    if not normalized:
        return None, "길이는 숫자로 입력해주세요. 예: `1`, `3`, `5`"

    try:
        duration = int(normalized)
    except ValueError:
        return None, "길이는 숫자로 입력해주세요. 예: `1`, `3`, `5`"

    if duration < MIN_DURATION_MINUTES:
        return None, "최소 길이는 1분이에요."

    if duration > MAX_DURATION_MINUTES:
        return MAX_DURATION_MINUTES, f"토큰 과사용을 막기 위해 최대 길이는 {MAX_DURATION_MINUTES}분으로 맞출게요."

    return duration, None
