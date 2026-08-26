"""USDA FoodData Central fallback nutrition lookup.

The app uses the local foods.csv first. When an image model recognizes a food
that is not in the local database, this module can look it up in USDA FoodData
Central using a key stored in Streamlit secrets as USDA_FDC_API_KEY.
"""

from typing import Optional, Dict, Any

import requests
import streamlit as st

API_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"


@st.cache_data(ttl=3600, show_spinner=False)
def search_usda_food(food_name: str) -> Optional[Dict[str, Any]]:
    api_key = st.secrets.get("USDA_FDC_API_KEY", "")
    if not api_key or not food_name.strip():
        return None

    try:
        response = requests.get(
            API_URL,
            params={
                "api_key": api_key,
                "query": food_name.strip(),
                "pageSize": 5,
            },
            timeout=8,
        )
        response.raise_for_status()
        foods = response.json().get("foods", [])
        if not foods:
            return None

        food = foods[0]
        nutrients = {
            n.get("nutrientName", "").lower(): n.get("value")
            for n in food.get("foodNutrients", [])
        }

        return {
            "name": food.get("description", food_name),
            "fdc_id": food.get("fdcId"),
            "calories": nutrients.get("energy") or nutrients.get("energy (kcal)"),
            "protein": nutrients.get("protein"),
            "carbs": nutrients.get("carbohydrate, by difference"),
            "fat": nutrients.get("total lipid (fat)"),
            "fiber": nutrients.get("fiber, total dietary"),
            "source": "USDA FoodData Central",
        }
    except (requests.RequestException, ValueError, TypeError):
        return None
