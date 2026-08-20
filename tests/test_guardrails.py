import pytest

from guardrails import MAX_DURATION_MINUTES, parse_duration_minutes, topic_guardrail_message


@pytest.mark.parametrize("topic", ["", "   "])
def test_topic_guardrail_rejects_empty_topic(topic: str) -> None:
    assert topic_guardrail_message(topic) is not None


@pytest.mark.parametrize("topic", ["과학", "우주", "아무거나"])
def test_topic_guardrail_rejects_broad_topic(topic: str) -> None:
    assert topic_guardrail_message(topic) is not None


@pytest.mark.parametrize(
    "topic",
    [
        "모기와 눈물",
        "눈물과 충치",
        "모기, 눈물",
        "모기 / 눈물",
        "모기 그리고 눈물",
    ],
)
def test_topic_guardrail_rejects_multiple_topics(topic: str) -> None:
    assert topic_guardrail_message(topic) is not None


def test_topic_guardrail_accepts_focused_science_question() -> None:
    assert topic_guardrail_message("돌고래는 어떻게 잠을 잘까요?") is None


@pytest.mark.parametrize(
    ("raw_text", "expected_duration", "expects_error"),
    [
        ("", None, True),
        ("세 분", None, True),
        ("0", None, True),
        ("1", 1, False),
        ("3", 3, False),
        (str(MAX_DURATION_MINUTES), MAX_DURATION_MINUTES, False),
        ("10", MAX_DURATION_MINUTES, True),
    ],
)
def test_parse_duration_minutes(
    raw_text: str,
    expected_duration: int | None,
    expects_error: bool,
) -> None:
    duration, message = parse_duration_minutes(raw_text)

    assert duration == expected_duration
    assert (message is not None) is expects_error
