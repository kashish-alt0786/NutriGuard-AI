"""Risk-aware context utilities for NutriGuard AI."""


def sanitize_risk(value, default=0.0):
    """Return a safe risk percentage in the inclusive range 0-100."""
    try:
        risk = float(value)
    except (TypeError, ValueError):
        return float(default)
    if not 0.0 <= risk <= 100.0:
        return float(default)
    return risk


def risk_label(risk):
    risk = sanitize_risk(risk)
    if risk < 30:
        return "Low"
    if risk < 60:
        return "Moderate"
    return "Elevated"


def build_nutrition_context(risk, meal_text=""):
    """Build transparent, deterministic nutrition guidance context."""
    risk = sanitize_risk(risk)
    label = risk_label(risk)
    meal = (meal_text or "").strip()

    if label == "Elevated":
        focus = (
            "Emphasize fiber-rich foods, vegetables, balanced portions and protein; "
            "limit sugary drinks and highly refined carbohydrates."
        )
        priority = "high-glycemic carbohydrate and added-sugar review"
    elif label == "Moderate":
        focus = (
            "Emphasize fiber, balanced portions, whole grains, vegetables and "
            "protein while limiting frequent sugary drinks and refined foods."
        )
        priority = "portion balance and carbohydrate quality"
    else:
        focus = "Use general balanced-meal guidance with vegetables, fiber and adequate protein."
        priority = "baseline nutritional balance"

    return {
        "risk": risk,
        "label": label,
        "focus": focus,
        "priority": priority,
        "meal": meal,
        "logic_trace": (
            f"Risk-aware rules activated for {risk:.1f}% ({label}). "
            f"Primary review: {priority}."
        ),
    }
