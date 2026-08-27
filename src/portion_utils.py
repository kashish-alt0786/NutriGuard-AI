"""Portion-scaling utilities for NutriGuard AI nutrition records."""


def scale_nutrition(record, grams: float, base_grams: float = 100.0):
    """Scale per-base-serving nutrition values to a requested gram amount."""
    if grams <= 0 or base_grams <= 0:
        raise ValueError("Serving size must be greater than zero.")
    factor = grams / base_grams
    return {
        "Calories": float(record.get("Calories", 0)) * factor,
        "Carbs": float(record.get("Carbs", 0)) * factor,
        "Protein": float(record.get("Protein", 0)) * factor,
        "Fat": float(record.get("Fat", 0)) * factor,
        "Fiber": float(record.get("Fiber", 0)) * factor,
        "GI": float(record.get("GI", 0)),
        "GL": float(record.get("GL", 0)) * factor,
    }
