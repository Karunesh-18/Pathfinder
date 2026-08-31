"""tfidf_rank — general-purpose TF-IDF cosine-similarity ranking.

This is a fresh implementation of the technique ARCHITECTURE.md's Section 01
identifies as the one legitimately reusable piece of the (nonexistent, in
this project) v3.py: TF-IDF vectorization + cosine similarity over course
text. There is no dataset-specific masking/reconstruction logic here — just
a query string ranked against a corpus of course text, which generalizes to
any course collection, not one templated dataset.

Public API: rank(query, courses) -> list of (course, score), sorted by score
descending. `courses` is a list of dicts each with at least an "id" and
enough text fields (title/description/skills_taught) to build a document.
"""

from __future__ import annotations

from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def _course_document(course: dict[str, Any]) -> str:
    """Flatten a course record into one text blob for vectorization."""
    parts = [
        course.get("title", ""),
        course.get("description", ""),
        " ".join(course.get("skills_taught", []) or []),
        course.get("level", ""),
    ]
    return " ".join(p for p in parts if p)


def tfidf_rank(query: str, courses: list[dict[str, Any]]) -> list[tuple[dict[str, Any], float]]:
    """Rank `courses` by TF-IDF cosine similarity to `query`.

    Returns a list of (course, similarity_score) tuples sorted by score
    descending. Score is in [0, 1]; 0 means no lexical overlap at all.
    """
    if not courses:
        return []

    documents = [_course_document(c) for c in courses]
    vectorizer = TfidfVectorizer(stop_words="english")
    # Fit on corpus + query together so the query's vocabulary is covered.
    tfidf_matrix = vectorizer.fit_transform(documents + [query])

    course_vectors = tfidf_matrix[:-1]
    query_vector = tfidf_matrix[-1]

    scores = cosine_similarity(query_vector, course_vectors)[0]

    ranked = sorted(zip(courses, scores), key=lambda pair: pair[1], reverse=True)
    return ranked
