import torch
from transformers import pipeline

MODEL_NAME = "nateraw/food"

# Food-101 class vocabulary used by the pretrained nateraw/food classifier.
# These are the model's learned labels; adding rows to the nutrition CSV does
# not change the classifier itself.
FOOD101_LABELS = [
    "apple_pie", "baby_back_ribs", "baklava", "beef_carpaccio", "beef_tartare",
    "beet_salad", "beignets", "bibimbap", "bread_pudding", "breakfast_burrito",
    "bruschetta", "caesar_salad", "cannoli", "caprese_salad", "carrot_cake",
    "ceviche", "cheesecake", "cheese_plate", "chicken_curry", "chicken_quesadilla",
    "chicken_wings", "chocolate_cake", "chocolate_mousse", "churros", "clam_chowder",
    "club_sandwich", "crab_cakes", "creme_brulee", "croque_madame", "cup_cakes",
    "deviled_eggs", "donuts", "dumplings", "edamame", "eggs_benedict", "escargots",
    "falafel", "filet_mignon", "fish_and_chips", "foie_gras", "french_fries",
    "french_onion_soup", "french_toast", "fried_calamari", "fried_rice", "frozen_yogurt",
    "garlic_bread", "gnocchi", "greek_salad", "grilled_cheese_sandwich", "grilled_salmon",
    "guacamole", "gyoza", "hamburger", "hot_and_sour_soup", "hot_dog", "huevos_rancheros",
    "hummus", "ice_cream", "lasagna", "lobster_bisque", "lobster_roll_sandwich",
    "macaroni_and_cheese", "macarons", "miso_soup", "mussels", "nachos", "omelette",
    "onion_rings", "oysters", "pad_thai", "paella", "pancakes", "panna_cotta",
    "peking_duck", "pho", "pizza", "pork_chop", "poutine", "prime_rib",
    "pulled_pork_sandwich", "ramen", "ravioli", "red_velvet_cake", "risotto", "samosa",
    "sashimi", "scallops", "seaweed_salad", "shrimp_and_grits", "spaghetti_bolognese",
    "spaghetti_carbonara", "spring_rolls", "steak", "strawberry_shortcake", "sushi",
    "tacos", "takoyaki", "tiramisu", "tuna_tartare", "waffles",
]

# Improve presentation without changing the underlying classifier class.
DISPLAY_LABELS = {
    "caesar_salad": "Caesar Salad",
    "creme_brulee": "Crème Brûlée",
    "cup_cakes": "Cupcakes",
    "french_fries": "French Fries",
    "french_toast": "French Toast",
    "fried_calamari": "Fried Calamari",
    "fried_rice": "Fried Rice",
    "grilled_cheese_sandwich": "Grilled Cheese Sandwich",
    "grilled_salmon": "Grilled Salmon",
    "hot_and_sour_soup": "Hot and Sour Soup",
    "ice_cream": "Ice Cream",
    "lobster_bisque": "Lobster Bisque",
    "lobster_roll_sandwich": "Lobster Roll Sandwich",
    "macaroni_and_cheese": "Macaroni and Cheese",
    "red_velvet_cake": "Red Velvet Cake",
    "seaweed_salad": "Seaweed Salad",
    "shrimp_and_grits": "Shrimp and Grits",
    "spaghetti_bolognese": "Spaghetti Bolognese",
    "spaghetti_carbonara": "Spaghetti Carbonara",
    "strawberry_shortcake": "Strawberry Shortcake",
    "tuna_tartare": "Tuna Tartare",
}

_classifier = None


def get_classifier():
    global _classifier

    if _classifier is None:
        _classifier = pipeline(
            "image-classification",
            model=MODEL_NAME,
        )

    return _classifier


def format_label(label):
    """Convert the pretrained Food-101 label into a user-friendly name."""
    raw = str(label).strip().lower()
    if raw in DISPLAY_LABELS:
        return DISPLAY_LABELS[raw]
    return raw.replace("_", " ").title()


def recognize_food(image, top_k=5):
    classifier = get_classifier()

    predictions = classifier(image, top_k=top_k)
    predictions = sorted(predictions, key=lambda x: x["score"], reverse=True)

    # Keep the model label intact for traceability while exposing a clean label
    # to the UI and nutrition matching layer.
    enriched_predictions = []
    for prediction in predictions:
        model_label = str(prediction["label"]).strip().lower()
        enriched_predictions.append(
            {
                **prediction,
                "model_label": model_label,
                "display_label": format_label(model_label),
            }
        )

    top_prediction = enriched_predictions[0]
    detected_food = top_prediction["display_label"]
    confidence = float(top_prediction["score"]) * 100

    return {
        "food": detected_food,
        "model_label": top_prediction["model_label"],
        "confidence": confidence,
        "predictions": enriched_predictions,
        "classifier": MODEL_NAME,
        "label_count": len(FOOD101_LABELS),
    }
