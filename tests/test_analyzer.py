from eda_log_ai.analyzer import analyze_log


def test_analyze_log_classifies_convergence_and_recommends_case():
    log = """
[WARN] Missing model parameter: vth0 in device nmos_1p8
[ERROR] SPICE simulation failed: convergence not reached
"""

    result = analyze_log(log)

    category_ids = {category.id for category in result.categories}
    assert "simulation_convergence" in category_ids
    assert "pdk_model_missing" in category_ids
    assert result.case_matches
    assert result.risk_level in {"medium", "high"}
    assert any("PDK" in recommendation or "model" in recommendation for recommendation in result.recommendations)


def test_analyze_log_handles_unknown_error():
    result = analyze_log("[ERROR] tool failed with strange internal condition 7788")

    assert result.categories[0].id == "unknown_eda_error"
    assert result.recommendations


def test_analyze_log_handles_clean_log():
    result = analyze_log("[INFO] simulation completed successfully")

    assert result.risk_level == "low"
    assert result.categories == ()
    assert result.case_matches == ()
    assert result.recommendations
