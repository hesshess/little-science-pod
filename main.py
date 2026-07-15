from pprint import pprint
from graph import build_graph


def main():
    graph = build_graph()

    approved_result = graph.invoke(
        {
            "age_group": "6-8",
            "topic": "the moon",
            "duration_minutes": 3,
            "tone": "playful",
            "review_status": "approve",
        }
    )

    revised_result = graph.invoke(
        {
            "age_group": "6-8",
            "topic": "rainbows",
            "duration_minutes": 3,
            "tone": "gentle",
            "review_status": "revise",
            "revision_request": "Use shorter sentences and more repetition.",
        }
    )

    print("=== Approved Path ===")
    pprint(approved_result)
    print("\n=== Revised Path ===")
    pprint(revised_result)


if __name__ == "__main__":
    main()
