from src.risk_context import build_nutrition_context, risk_label, sanitize_risk


def test_risk_validation():
    assert sanitize_risk("74.2") == 74.2
    assert sanitize_risk("not-a-number") == 0.0
    assert sanitize_risk(150) == 0.0
    assert sanitize_risk(-5) == 0.0


def test_risk_bands():
    assert risk_label(29.9) == "Low"
    assert risk_label(30) == "Moderate"
    assert risk_label(59.9) == "Moderate"
    assert risk_label(60) == "Elevated"


def test_context_changes_with_risk():
    low = build_nutrition_context(10, "rice")
    high = build_nutrition_context(80, "rice")
    assert low["label"] == "Low"
    assert high["label"] == "Elevated"
    assert low["priority"] != high["priority"]
    assert high["meal"] == "rice"
