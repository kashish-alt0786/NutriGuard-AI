import torch
from transformers import pipeline

# Primary classifier: Food-101 provides 101 learned food categories.
MODEL_NAME = "nateraw/food"
# Broad zero-shot fallback: CLIP can compare an image against a much larger
# vocabulary without requiring a new classifier head for every food name.
BROAD_MODEL_NAME = "openai/clip-vit-base-patch32"

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

# A broad everyday-food vocabulary for zero-shot image matching. This is not
# a claim that CLIP can recognize every food perfectly; it gives the app a
# much wider search space than the fixed Food-101 classifier.
BROAD_FOOD_LABELS = [
    "apple", "banana", "orange", "mango", "grapes", "strawberry", "blueberry", "raspberry",
    "watermelon", "pineapple", "papaya", "guava", "kiwi", "peach", "pear", "plum",
    "pomegranate", "coconut", "lemon", "lime", "avocado", "tomato", "potato", "sweet potato",
    "onion", "garlic", "ginger", "carrot", "cucumber", "broccoli", "cauliflower", "spinach",
    "lettuce", "cabbage", "peas", "green beans", "bell pepper", "chili pepper", "beetroot",
    "corn", "mushroom", "eggplant", "okra", "pumpkin", "zucchini", "celery", "radish",
    "rice", "brown rice", "fried rice", "biryani", "pulao", "risotto", "porridge", "oatmeal",
    "oats", "quinoa", "bread", "whole wheat bread", "toast", "naan", "roti", "chapati",
    "paratha", "puri", "dosa", "idli", "uttapam", "upma", "poha", "pancake", "waffle",
    "cereal", "pasta", "spaghetti", "macaroni", "noodles", "ramen", "lasagna", "ravioli",
    "pizza", "burger", "sandwich", "hot dog", "french fries", "potato wedges", "nachos",
    "taco", "burrito", "quesadilla", "samosa", "spring roll", "dumpling", "momo", "falafel",
    "hummus", "chickpeas", "lentils", "dal", "kidney beans", "black beans", "soybeans", "edamame",
    "tofu", "paneer", "cheese", "yogurt", "curd", "milk", "butter", "cream", "ice cream",
    "egg", "boiled egg", "omelette", "scrambled eggs", "chicken", "grilled chicken", "fried chicken",
    "chicken curry", "chicken tikka", "chicken biryani", "chicken wings", "turkey", "beef", "steak",
    "beef curry", "pork", "pork chop", "bacon", "ham", "lamb", "mutton", "fish", "grilled fish",
    "fried fish", "salmon", "tuna", "sardines", "anchovies", "shrimp", "prawns", "crab", "lobster",
    "mussels", "oysters", "sushi", "sashimi", "curry", "vegetable curry", "chana masala", "rajma",
    "butter chicken", "palak paneer", "tandoori chicken", "dal makhani", "naan bread", "chole bhature",
    "pav bhaji", "vada pav", "aloo paratha", "masala dosa", "idli sambar", "sambar", "rasam",
    "tomato soup", "lentil soup", "chicken soup", "vegetable soup", "salad", "caesar salad", "greek salad",
    "fruit salad", "coleslaw", "guacamole", "salsa", "peanut butter", "almonds", "walnuts", "cashews",
    "peanuts", "pistachios", "dates", "raisins", "dark chocolate", "chocolate", "chocolate cake",
    "vanilla cake", "red velvet cake", "carrot cake", "cheesecake", "brownie", "cookie", "donut",
    "muffin", "cupcake", "croissant", "pastry", "baklava", "tiramisu", "panna cotta", "custard",
    "pudding", "fruit tart", "apple pie", "popcorn", "chips", "crackers", "pretzel", "granola",
    "smoothie", "fruit juice", "coffee", "tea", "green tea", "coconut water",
]

DISPLAY_LABELS = {
    "caesar_salad": "Caesar Salad", "creme_brulee": "Crème Brûlée", "cup_cakes": "Cupcakes",
    "french_fries": "French Fries", "french_toast": "French Toast", "fried_calamari": "Fried Calamari",
    "fried_rice": "Fried Rice", "grilled_cheese_sandwich": "Grilled Cheese Sandwich",
    "grilled_salmon": "Grilled Salmon", "hot_and_sour_soup": "Hot and Sour Soup",
    "ice_cream": "Ice Cream", "lobster_bisque": "Lobster Bisque",
    "lobster_roll_sandwich": "Lobster Roll Sandwich", "macaroni_and_cheese": "Macaroni and Cheese",
    "red_velvet_cake": "Red Velvet Cake", "seaweed_salad": "Seaweed Salad",
    "shrimp_and_grits": "Shrimp and Grits", "spaghetti_bolognese": "Spaghetti Bolognese",
    "spaghetti_carbonara": "Spaghetti Carbonara", "strawberry_shortcake": "Strawberry Shortcake",
    "tuna_tartare": "Tuna Tartare",
}

_classifier = None
_broad_classifier = None


def get_classifier():
    global _classifier
    if _classifier is None:
        _classifier = pipeline("image-classification", model=MODEL_NAME)
    return _classifier


def get_broad_classifier():
    global _broad_classifier
    if _broad_classifier is None:
        _broad_classifier = pipeline("zero-shot-image-classification", model=BROAD_MODEL_NAME)
    return _broad_classifier


def format_label(label):
    raw = str(label).strip().lower()
    return DISPLAY_LABELS.get(raw, raw.replace("_", " ").title())


def recognize_food(image, top_k=5, broad_fallback=True):
    """Recognize food using Food-101, with a broad CLIP vocabulary fallback.

    The fallback is intentionally described as zero-shot matching rather than
    a newly trained classifier. It broadens the vocabulary but does not make
    a guarantee of perfect recognition for arbitrary foods or mixed dishes.
    """
    classifier = get_classifier()
    predictions = sorted(classifier(image, top_k=top_k), key=lambda x: x["score"], reverse=True)

    enriched = []
    for prediction in predictions:
        model_label = str(prediction["label"]).strip().lower()
        enriched.append({
            **prediction,
            "model_label": model_label,
            "display_label": format_label(model_label),
            "recognition_source": "Food-101",
        })

    top = enriched[0]
    food101_confidence = float(top["score"]) * 100

    # Use the broader CLIP vocabulary when Food-101 is uncertain. This avoids
    # pretending an unrelated Food-101 class is a confident recognition.
    if broad_fallback and food101_confidence < 70.0:
        broad = get_broad_classifier()
        broad_predictions = broad(image, candidate_labels=BROAD_FOOD_LABELS)
        broad_predictions = sorted(broad_predictions, key=lambda x: x["score"], reverse=True)[:top_k]
        broad_enriched = [
            {
                "label": p["label"],
                "score": float(p["score"]),
                "model_label": p["label"],
                "display_label": p["label"].title(),
                "recognition_source": "CLIP zero-shot",
            }
            for p in broad_predictions
        ]
        if broad_enriched and broad_enriched[0]["score"] > 0:
            broad_top = broad_enriched[0]
            return {
                "food": broad_top["display_label"],
                "model_label": broad_top["model_label"],
                "confidence": broad_top["score"] * 100,
                "predictions": broad_enriched,
                "classifier": BROAD_MODEL_NAME,
                "label_count": len(BROAD_FOOD_LABELS),
                "recognition_mode": "broad zero-shot fallback",
                "food101_confidence": food101_confidence,
            }

    return {
        "food": top["display_label"],
        "model_label": top["model_label"],
        "confidence": food101_confidence,
        "predictions": enriched,
        "classifier": MODEL_NAME,
        "label_count": len(FOOD101_LABELS),
        "recognition_mode": "Food-101",
        "food101_confidence": food101_confidence,
    }
