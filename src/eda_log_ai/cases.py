from __future__ import annotations

import json
from pathlib import Path

from eda_log_ai.models import CaseMatch, ErrorCategory, LogEvent

DEFAULT_CASES_PATH = Path(__file__).resolve().parents[2] / "knowledge_base" / "cases.json"


def load_cases(path: Path | None = None) -> list[dict[str, object]]:
    case_path = path or DEFAULT_CASES_PATH
    with case_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError("case database must be a JSON array")
    return data


def retrieve_cases(
    events: tuple[LogEvent, ...],
    categories: tuple[ErrorCategory, ...],
    *,
    case_path: Path | None = None,
    limit: int = 3,
) -> tuple[CaseMatch, ...]:
    cases = load_cases(case_path)
    query_terms = _query_terms(events, categories)
    category_ids = {category.id for category in categories}
    strong_terms = {
        value.lower()
        for event in events
        for value in (event.code, event.entity)
        if value
    }

    matches: list[CaseMatch] = []
    for case in cases:
        tags = tuple(str(tag) for tag in case.get("tags", []))
        haystack = " ".join(
            str(case.get(field, "")) for field in ("title", "symptoms", "root_cause", "fix")
        ).lower()
        tag_score = len(category_ids.intersection(tags)) * 4
        strong_score = sum(3 for term in strong_terms if term in haystack)
        term_score = sum(1 for term in query_terms if term and term in haystack)
        if tag_score == 0 and strong_score == 0:
            continue
        score = tag_score + strong_score + term_score
        if score < 4:
            continue
        matches.append(
            CaseMatch(
                case_id=str(case["id"]),
                title=str(case["title"]),
                score=round(score / 10, 2),
                root_cause=str(case["root_cause"]),
                fix=str(case["fix"]),
                tags=tags,
            )
        )

    return tuple(sorted(matches, key=lambda match: match.score, reverse=True)[:limit])


def _query_terms(events: tuple[LogEvent, ...], categories: tuple[ErrorCategory, ...]) -> set[str]:
    terms = {category.id.replace("_", " ") for category in categories}
    for event in events:
        for value in (event.code, event.entity, event.tool):
            if value:
                terms.add(value.lower())
        for token in event.message.lower().replace(":", " ").replace("=", " ").split():
            if len(token) >= 5:
                terms.add(token.strip("[](),;"))
    return terms
