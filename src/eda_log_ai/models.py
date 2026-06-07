from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Severity(str, Enum):
    FATAL = "FATAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class LogEvent:
    line_no: int
    raw: str
    severity: Severity
    message: str
    tool: str | None = None
    code: str | None = None
    file_path: str | None = None
    entity: str | None = None


@dataclass(frozen=True)
class ErrorCategory:
    id: str
    title: str
    confidence: float
    evidence_lines: tuple[int, ...]


@dataclass(frozen=True)
class CaseMatch:
    case_id: str
    title: str
    score: float
    root_cause: str
    fix: str
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class AnalysisResult:
    summary: str
    risk_level: str
    events: tuple[LogEvent, ...]
    categories: tuple[ErrorCategory, ...]
    case_matches: tuple[CaseMatch, ...]
    recommendations: tuple[str, ...]
    escalation: str
    assumptions: tuple[str, ...] = field(default_factory=tuple)
