from __future__ import annotations

import re
from collections import defaultdict

from eda_log_ai.models import ErrorCategory, LogEvent, Severity


CATEGORY_RULES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("simulation_convergence", "Simulation convergence failure", ("convergence", "timestep too small", "singular matrix", "newton")),
    ("pdk_model_missing", "PDK/model include or parameter issue", ("missing model", "model parameter", "model include", "pdk", "vth0", "corner")),
    ("netlist_reference", "Netlist library/subckt reference issue", ("undefined subckt", "unknown subckt", "undefined cell", "cannot find cell")),
    ("physical_verification", "DRC/LVS physical verification issue", ("spacing violation", "lvs mismatch", "layout short", "layout open", "net mismatch", "rule deck mismatch")),
    ("license_environment", "License or runtime environment issue", ("license", "lmgrd", "checkout failed", "feature not found")),
    ("resource_limit", "Runtime resource limit issue", ("out of memory", "memory", "disk full", "timeout", "killed")),
)


def classify_events(events: tuple[LogEvent, ...]) -> tuple[ErrorCategory, ...]:
    scores: dict[str, float] = defaultdict(float)
    evidence: dict[str, list[int]] = defaultdict(list)
    titles = {rule_id: title for rule_id, title, _ in CATEGORY_RULES}

    for event in events:
        text = event.message.lower()
        severity_weight = _severity_weight(event.severity)
        for rule_id, _title, keywords in CATEGORY_RULES:
            hits = sum(1 for keyword in keywords if re.search(re.escape(keyword), text))
            if hits:
                scores[rule_id] += hits * severity_weight
                evidence[rule_id].append(event.line_no)

    categories: list[ErrorCategory] = []
    if scores:
        max_score = max(scores.values())
        for rule_id, score in sorted(scores.items(), key=lambda item: item[1], reverse=True):
            confidence = min(0.95, 0.35 + 0.6 * (score / max_score))
            categories.append(
                ErrorCategory(
                    id=rule_id,
                    title=titles[rule_id],
                    confidence=round(confidence, 2),
                    evidence_lines=tuple(sorted(set(evidence[rule_id]))),
                )
            )

    if not categories and events:
        error_lines = tuple(event.line_no for event in events if event.severity in {Severity.ERROR, Severity.FATAL})
        categories.append(ErrorCategory("unknown_eda_error", "Unclassified EDA tool error", 0.4, error_lines))

    return tuple(categories)


def _severity_weight(severity: Severity) -> float:
    if severity == Severity.FATAL:
        return 2.0
    if severity == Severity.ERROR:
        return 1.5
    if severity == Severity.WARNING:
        return 1.0
    return 0.3
