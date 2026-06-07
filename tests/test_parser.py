from eda_log_ai.parser import parse_log
from eda_log_ai.models import Severity


def test_parse_log_extracts_errors_and_context():
    log = "\n".join(
        [
            "[INFO] start",
            "[WARN] Missing model parameter: vth0 in device nmos_1p8",
            "[ERROR] SPICE simulation failed: convergence not reached",
            "[INFO] done",
        ]
    )

    events = parse_log(log)

    assert any(event.severity == Severity.ERROR for event in events)
    assert any(event.entity == "vth0" for event in events)
    assert any(event.line_no == 3 and event.tool == "spice" for event in events)
