from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from enum import Enum

from eda_log_ai.models import AnalysisResult


def to_json(result: AnalysisResult) -> str:
    return json.dumps(_normalize(result), ensure_ascii=False, indent=2)


def to_text(result: AnalysisResult) -> str:
    lines = [
        "EDA Log AI Analysis",
        "=" * 19,
        f"Summary: {result.summary}",
        f"Risk level: {result.risk_level}",
        "",
        "Categories:",
    ]
    for category in result.categories:
        evidence = ", ".join(str(line) for line in category.evidence_lines) or "n/a"
        lines.append(f"- {category.title} ({category.confidence:.2f}), evidence lines: {evidence}")

    lines.extend(["", "Key events:"])
    for event in result.events:
        if event.severity.value in {"ERROR", "FATAL", "WARNING"}:
            lines.append(f"- line {event.line_no} [{event.severity.value}]: {event.message}")

    lines.extend(["", "Historical case matches:"])
    if result.case_matches:
        for match in result.case_matches:
            lines.append(f"- {match.case_id} {match.title} (score {match.score:.2f})")
            lines.append(f"  root cause: {match.root_cause}")
            lines.append(f"  fix: {match.fix}")
    else:
        lines.append("- none")

    lines.extend(["", "Recommended next steps:"])
    for index, recommendation in enumerate(result.recommendations, start=1):
        lines.append(f"{index}. {recommendation}")

    lines.extend(["", f"Escalation: {result.escalation}"])
    return "\n".join(lines)


def _normalize(value):
    if is_dataclass(value):
        return {key: _normalize(item) for key, item in asdict(value).items()}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, tuple):
        return [_normalize(item) for item in value]
    if isinstance(value, list):
        return [_normalize(item) for item in value]
    if isinstance(value, dict):
        return {key: _normalize(item) for key, item in value.items()}
    return value
