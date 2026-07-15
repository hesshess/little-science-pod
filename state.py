from typing import Literal, TypedDict


class EpisodeState(TypedDict, total=False):
    topic: str
    duration_minutes: int
    tone: str
    generate_audio: bool
    output_dir: str
    review_status: Literal["approve", "revise"]
    revision_request: str
    plan: str
    science_fact: str
    parent_tip: str
    script: str
    doctor_lines: list[str]
    doctor_audio_path: str
    final_audio_path: str
    parent_summary: str
