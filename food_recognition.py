import torch
from transformers import pipeline

MODEL_NAME = "nateraw/food"

_classifier = None


def get_classifier():
    global _classifier

    if _classifier is None:
        _classifier = pipeline(
            "image-classification",
            model=MODEL_NAME
        )

    return _classifier


def recognize_food(image, top_k=5):
    classifier = get_classifier()

    predictions = classifier(
        image,
        top_k=top_k
    )

    predictions = sorted(
        predictions,
        key=lambda x: x["score"],
        reverse=True
    )

    top_prediction = predictions[0]

    detected_food = (
        top_prediction["label"]
        .replace("_", " ")
        .title()
    )

    confidence = top_prediction["score"] * 100

    return {
        "food": detected_food,
        "confidence": confidence,
        "predictions": predictions
    }
