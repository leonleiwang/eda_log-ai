from __future__ import annotations

import re

from eda_log_ai.models import LogEvent, Severity

SEVERITY_PATTERNS: tuple[tuple[Severity, re.Pattern[str]], ...] = (
    (Severity.FATAL, re.compile(r"\b(FATAL|CRITICAL)\b", re.IGNORECASE)),
    (Severity.ERROR, re.compile(r"\b(ERROR|ERR|FAILED|FAILURE)\b", re.IGNORECASE)),
    (Severity.WARNING, re.compile(r"\b(WARN|WARNING)\b", re.IGNORECASE)),
    (Severity.INFO, re.compile(r"\b(INFO|NOTE)\b", re.IGNORECASE)),
)

TOOL_PATTERN = re.compile(r"\b(spice|spectre|hspice|ngspice|drc|lvs|calibre|innovus|virtuoso|pdk|license)\b", re.IGNORECASE)
CODE_PATTERN = re.compile(r"\b([A-Z]{2,8}[-_]\d{3,6}|[A-Z]{2,8}\d{3,6})\b")
PATH_PATTERN = re.compile(r"([A-Za-z]:\\[^\s:]+|/[^ \t:]+)")
ENTITY_PATTERNS = (
    re.compile(r"\bmissing\s+model\s+parameter\s*[:=]?\s*([A-Za-z_][\w.$:-]*)", re.IGNORECASE),
    re.compile(r"\b(subckt|cell|device|instance|model)\s+['\"]?([A-Za-z_][\w.$:-]*)", re.IGNORECASE),
    re.compile(r"\bundefined\s+(?:subckt|cell)\s+['\"]?([A-Za-z_][\w.$:-]*)", re.IGNORECASE),
)


def parse_log(log_text: str, *, context_window: int = 1) -> tuple[LogEvent, ...]:
    """Extract relevant log events while preserving line numbers."""
    lines = log_text.splitlines()
    interesting: dict[int, LogEvent] = {}

    for index, line in enumerate(lines, start=1):
        severity = _detect_severity(line)
        if severity in {Severity.FATAL, Severity.ERROR, Severity.WARNING}:
            interesting[index] = _event_from_line(index, line, severity)
            for neighbor in range(max(1, index - context_window), min(len(lines), index + context_window) + 1):
                if neighbor not in interesting and neighbor != index:
                    interesting[neighbor] = _event_from_line(neighbor, lines[neighbor - 1], Severity.INFO)

    return tuple(interesting[key] for key in sorted(interesting))


def _detect_severity(line: str) -> Severity:
    for severity, pattern in SEVERITY_PATTERNS:
        if pattern.search(line):
            return severity
    return Severity.UNKNOWN


def _event_from_line(line_no: int, raw: str, severity: Severity) -> LogEvent:
    tool = _first_group(TOOL_PATTERN, raw)
    code = _first_group(CODE_PATTERN, raw)
    file_path = _first_group(PATH_PATTERN, raw)
    entity = _extract_entity(raw)
    message = raw.strip()
    return LogEvent(
        line_no=line_no,
        raw=raw,
        severity=severity,
        message=message,
        tool=tool.lower() if tool else None,
        code=code,
        file_path=file_path,
        entity=entity,
    )


def _first_group(pattern: re.Pattern[str], text: str) -> str | None:
    match = pattern.search(text)
    return match.group(1) if match else None


def _extract_entity(text: str) -> str | None:
    for pattern in ENTITY_PATTERNS:
        match = pattern.search(text)
        if not match:
            continue
        return match.group(match.lastindex or 1)
    return None
