from typing import Literal, TypedDict


class EpisodeState(TypedDict, total=False):
    age_group: str
    topic: str
    duration_minutes: int
    tone: str
    review_status: Literal["approve", "revise"]
    revision_request: str
    plan: str
    science_fact: str
    target_words: list[str]
    parent_tip: str
    script: str
    parent_summary: str
