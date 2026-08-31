"""Test harness for the Retrieval & Ranking Service prototype.

Takes a sample learner query, retrieves candidate courses from the Course &
Skills Knowledge Base (Postgres/Supabase if configured, SQLite otherwise —
see stores/course-knowledge-base/db.py), ranks them with tfidf_rank, and
prints the ranked list with similarity scores for a by-eye sanity check.

Usage (run ingest.py first to populate the store):
    python stores/course-knowledge-base/ingest.py
    python services/retrieval-ranking/test_harness.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.console import fix_windows_console_encoding  # noqa: E402

fix_windows_console_encoding()

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rank import tfidf_rank  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "stores" / "course-knowledge-base"))
import db  # noqa: E402

# A sample learner query, standing in for what the (not-yet-built) Skill-Gap
# Analysis Agent would hand this service for one identified gap.
SAMPLE_QUERIES = [
    "I want to learn how to build data pipelines and ETL workflows with Python and SQL",
    "orchestrating scheduled workflows with Apache Airflow",
    "getting started with distributed big data processing using Spark",
]


def main() -> None:
    courses = db.list_courses()
    print(f"Loaded {len(courses)} courses (backend: {db.backend_name()})\n")

    for query in SAMPLE_QUERIES:
        print("=" * 78)
        print(f"Learner query: {query!r}")
        print("-" * 78)
        ranked = tfidf_rank(query, courses)
        for i, (course, score) in enumerate(ranked[:5], start=1):
            print(f"{i}. [{score:.3f}] {course['title']}  ({course['provider']})")
            print(f"   skills: {', '.join(course['skills_taught'])}")
        print()


if __name__ == "__main__":
    main()
