import pytest

from nodes import route_after_review, route_after_summary


@pytest.mark.parametrize("review_status", ["approve", "revise"])
def test_route_after_review_uses_review_status(review_status: str) -> None:
    assert route_after_review({"review_status": review_status}) == review_status


@pytest.mark.parametrize(
    ("generate_audio", "expected_route"),
    [
        (True, "audio"),
        (False, "done"),
    ],
)
def test_route_after_summary_follows_audio_choice(
    generate_audio: bool,
    expected_route: str,
) -> None:
    assert route_after_summary({"generate_audio": generate_audio}) == expected_route


def test_route_after_summary_defaults_to_done() -> None:
    assert route_after_summary({}) == "done"
