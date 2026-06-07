from __future__ import annotations

from pathlib import Path

from eda_log_ai.cases import retrieve_cases
from eda_log_ai.classifier import classify_events
from eda_log_ai.models import AnalysisResult, ErrorCategory, LogEvent, Severity
from eda_log_ai.parser import parse_log


def analyze_log(log_text: str, *, case_path: Path | None = None) -> AnalysisResult:
    events = parse_log(log_text)
    categories = classify_events(events)
    case_matches = retrieve_cases(events, categories, case_path=case_path)
    recommendations = _recommend(categories, case_matches, events)
    risk_level = _risk_level(events, categories)
    escalation = _escalation(categories)
    summary = _summary(events, categories, case_matches)
    assumptions = (
        "The log is analyzed as a single run; cross-run history is not available unless represented in the case database.",
        "Recommendations are triage hints and should be confirmed by the responsible EDA engineer before project files are modified.",
    )
    return AnalysisResult(summary, risk_level, events, categories, case_matches, recommendations, escalation, assumptions)


def analyze_file(path: Path, *, case_path: Path | None = None) -> AnalysisResult:
    return analyze_log(path.read_text(encoding="utf-8"), case_path=case_path)


def _summary(
    events: tuple[LogEvent, ...],
    categories: tuple[ErrorCategory, ...],
    case_matches: tuple,
) -> str:
    error_count = sum(1 for event in events if event.severity in {Severity.ERROR, Severity.FATAL})
    warning_count = sum(1 for event in events if event.severity == Severity.WARNING)
    top = categories[0].title if categories else "No obvious EDA error pattern"
    case_text = f"; matched {len(case_matches)} historical case(s)" if case_matches else "; no strong historical case match"
    return f"Detected {error_count} error/fatal event(s) and {warning_count} warning(s). Primary category: {top}{case_text}."


def _risk_level(events: tuple[LogEvent, ...], categories: tuple[ErrorCategory, ...]) -> str:
    if any(event.severity == Severity.FATAL for event in events):
        return "high"
    if any(category.confidence >= 0.8 for category in categories):
        return "medium"
    if any(event.severity == Severity.ERROR for event in events):
        return "medium"
    return "low"


def _escalation(categories: tuple[ErrorCategory, ...]) -> str:
    ids = {category.id for category in categories}
    if "license_environment" in ids:
        return "Escalate to CAD/IT license owner if license server status cannot be confirmed locally."
    if "pdk_model_missing" in ids:
        return "Escalate to PDK/model owner if include paths and PDK version are correct but parameters remain missing."
    if "physical_verification" in ids:
        return "Escalate to physical verification/layout engineer after checking rule deck version and extracted layout inputs."
    if "simulation_convergence" in ids:
        return "Escalate to simulation/modeling engineer if model setup is correct but convergence remains unstable."
    return "Escalate to the tool owner with the extracted evidence lines and full raw log."


def _recommend(
    categories: tuple[ErrorCategory, ...],
    case_matches: tuple,
    events: tuple[LogEvent, ...],
) -> tuple[str, ...]:
    recommendations: list[str] = []
    by_category = {
        "pdk_model_missing": "Check PDK/model include paths, selected process corner, and whether the referenced model parameters exist in the loaded library.",
        "netlist_reference": "Verify the referenced subckt/cell exists in the library list and that the netlist include order matches the simulator requirements.",
        "simulation_convergence": "Review initial conditions, timestep settings, device model validity, and recent netlist changes around the failing instance.",
        "physical_verification": "Confirm DRC/LVS rule deck version, layout/netlist pair, extraction options, and whether reported layers map to the active PDK.",
        "license_environment": "Check license feature name, server reachability, expiry, and concurrent checkout usage before rerunning the EDA tool.",
        "resource_limit": "Inspect memory/disk/runtime limits and rerun with smaller partitions or adjusted job resource requests.",
    }

    for category in categories:
        recommendation = by_category.get(category.id)
        if recommendation and recommendation not in recommendations:
            recommendations.append(recommendation)

    if case_matches:
        top_case = case_matches[0]
        recommendations.append(f"Compare against historical case {top_case.case_id}: {top_case.fix}")

    evidence_lines = [str(event.line_no) for event in events if event.severity in {Severity.ERROR, Severity.FATAL}]
    if evidence_lines:
        recommendations.append("Attach evidence lines " + ", ".join(evidence_lines[:8]) + " when escalating or filing an internal issue.")

    return tuple(recommendations or ("No strong rule hit; preserve the full log and ask the tool owner to classify this new pattern.",))
