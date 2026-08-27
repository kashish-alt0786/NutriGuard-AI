import streamlit as st
import pandas as pd
from pathlib import Path

from food_recognition import recognize_food
from src.risk_context import build_nutrition_context, sanitize_risk
from src.usda_nutrition import search_usda_food
from src.portion_utils import scale_nutrition

ROOT = Path(__file__).parent
st.set_page_config(page_title="NutriGuard AI", page_icon="🥗", layout="wide")


def load_food_database():
    frames = []
    for filename in ("foods.csv", "everyday_foods.csv"):
        path = ROOT / filename
        if path.exists():
            frames.append(pd.read_csv(path))
    if not frames:
        return pd.DataFrame(columns=["English", "Category", "Calories", "Carbs", "Protein", "Fat", "Fiber", "GI", "GL", "HealthySwap", "Why"])
    combined = pd.concat(frames, ignore_index=True)
    combined["English"] = combined["English"].astype(str).str.strip()
    combined = combined[combined["English"].ne("")].drop_duplicates(subset=["English"], keep="first").copy()
    combined["food_key"] = combined["English"].str.lower()
    return combined


foods = load_food_database()

st.info("ℹ️ **Educational research tool:** NutriGuard AI provides general nutrition information and is not a medical diagnostic or treatment tool.")

query = st.query_params
risk_from_predictor = None
risk_source = ""
if "risk" in query:
    risk_from_predictor = sanitize_risk(query.get("risk"), default=0.0)
    risk_source = str(query.get("source", "")).strip()

with st.sidebar:
    st.markdown("## 🥗 NutriGuard AI")
    st.caption("Risk-aware educational nutrition analysis")
    st.divider()
    st.markdown("**Input flow**")
    st.markdown("1. Confirm risk profile\n2. Add a meal photo or ingredients\n3. Set serving size\n4. Generate analysis")
    st.divider()
    st.caption(f"Food database: **{len(foods):,} records**")
    st.caption("Image recognition: **Food-101 + broad zero-shot vocabulary**")

st.title("🥗 NutriGuard AI")
st.subheader("Risk-Aware Nutrition Intelligence")
st.caption("Connect your diabetes-risk profile with a transparent meal analysis.")

st.divider()
st.header("🩺 1. My Risk Profile")
if "risk_profile" not in st.session_state:
    st.session_state.risk_profile = risk_from_predictor if risk_from_predictor is not None else 50.0

if risk_from_predictor is not None:
    label = "Low" if risk_from_predictor < 30 else "Moderate" if risk_from_predictor < 60 else "Elevated"
    source_text = " from the Diabetes Risk Predictor" if risk_source == "diabetes-risk-predictor" else " through the risk handoff"
    st.success(f"🔗 **Connected risk: {risk_from_predictor:.1f}% — {label.upper()}**")
    st.caption(f"Validated statistical model output received{source_text}.")
    use_connected = st.radio("Use the connected result?", ["Yes — use my predictor result", "No — enter another estimate"], horizontal=True)
else:
    use_connected = "No — enter another estimate"

if risk_from_predictor is not None and use_connected.startswith("Yes"):
    risk_percentage = float(risk_from_predictor)
    st.session_state.risk_profile = risk_percentage
else:
    risk_percentage = st.slider("Estimated diabetes risk (%)", 0, 100, int(round(st.session_state.risk_profile)), 1)
    st.session_state.risk_profile = float(risk_percentage)

risk_context = build_nutrition_context(risk_percentage)
risk_label = risk_context["label"].upper()
risk_icon = "🟢" if risk_label == "LOW" else "🟡" if risk_label == "MODERATE" else "🔴"
st.metric("Estimated Risk Profile", f"{risk_percentage:.0f}%", f"{risk_icon} {risk_label}")

st.divider()
st.header("🥗 2. My Meal")
st.write("Upload a meal photo, enter ingredients, or use both. NutriGuard checks the expanded local food database first and can use USDA FoodData Central when configured.")
image_col, manual_col = st.columns(2)
with image_col:
    st.subheader("📷 Upload Your Meal")
    uploaded_image = st.file_uploader("Upload meal image", type=["jpg", "jpeg", "png"])
with manual_col:
    st.subheader("✍️ Describe Your Meal")
    manual_ingredients = st.text_area("Enter or edit ingredients", placeholder="Example: rice, grilled chicken, broccoli", height=150)

ai_food = None
ai_confidence = None
recognition = None
if uploaded_image is not None:
    from PIL import Image
    image = Image.open(uploaded_image).convert("RGB")
    st.image(image, caption="Uploaded meal image", use_container_width=True)
    try:
        with st.spinner("🤖 Recognizing the meal..."):
            recognition = recognize_food(image, top_k=5)
        ai_food = recognition["food"]
        ai_confidence = float(recognition["confidence"])
        st.success(f"🍽️ Detected food: **{ai_food}**")
        source_name = recognition.get("recognition_mode", "pretrained image recognition")
        st.caption(f"Recognition route: **{source_name}** · Model: `{recognition['classifier']}` · Search vocabulary: **{recognition['label_count']} food labels**")
        if recognition.get("recognition_mode") == "broad zero-shot fallback":
            st.info("🌎 Broad recognition was activated because the fixed Food-101 classifier was uncertain. Please verify the detected food before analysis.")
        st.metric("🎯 Recognition Confidence", f"{ai_confidence:.2f}%")
        with st.expander("🔎 View top predictions"):
            for i, prediction in enumerate(recognition["predictions"], 1):
                display_label = prediction.get("display_label", str(prediction["label"]).replace("_", " ").title())
                st.write(f"{i}. **{display_label}** — {prediction['score'] * 100:.2f}%")
    except Exception as exc:
        st.error("The image could not be analyzed. Please try a clearer meal photo or enter the food name manually.")
        st.caption(f"Technical detail: {type(exc).__name__}")

if ai_confidence is not None and ai_confidence < 70:
    st.warning(f"⚠️ Recognition confidence is {ai_confidence:.2f}%. Please verify the detected food before generating the analysis.")

FOOD_ALIASES = {
    "chicken": "Chicken Breast", "chicken breast": "Chicken Breast", "grilled chicken": "Grilled Chicken",
    "fish": "Grilled Fish", "prawn": "Prawns", "prawns": "Prawns", "shrimp": "Prawns",
    "egg": "Egg", "eggs": "Egg", "rice": "White Rice", "white rice": "White Rice", "brown rice": "Brown Rice",
    "roti": "Roti", "chapati": "Chapati", "dal": "Dal Tadka", "lentils": "Lentil Soup",
    "chickpeas": "Chickpea Salad", "chana": "Chickpea Salad", "beans": "Kidney Beans", "kidney beans": "Kidney Beans",
    "rajma": "Rajma Chawal", "potato": "Potato", "potatoes": "Potato", "sweet potato": "Sweet Potato",
    "oats": "Oats", "yogurt": "Plain Yogurt", "curd": "Curd", "milk": "Milk", "paneer": "Paneer",
    "bread": "Whole Wheat Bread", "whole wheat bread": "Whole Wheat Bread", "apple": "Apple", "banana": "Banana",
    "orange": "Orange", "mango": "Mango", "avocado": "Avocado", "tomato": "Tomato", "spinach": "Spinach",
    "broccoli": "Broccoli", "cauliflower": "Cauliflower", "carrot": "Carrot", "cucumber": "Cucumber",
    "corn": "Sweet Corn", "popcorn": "Popcorn", "almonds": "Almonds", "peanuts": "Peanuts", "walnuts": "Walnuts",
    "cashews": "Cashews", "pizza": "Pizza", "burger": "Burger", "pasta": "Pasta", "noodles": "Noodles",
    "fries": "French Fries", "ice cream": "Ice Cream",
}


def find_local_food(name: str):
    key = name.strip().lower()
    if not key:
        return None, "unmatched"
    canonical = FOOD_ALIASES.get(key, name.strip())
    canonical_key = canonical.lower()
    exact = foods[foods["food_key"] == canonical_key]
    if len(exact):
        return exact.iloc[0], "alias" if key != canonical_key else "exact"
    exact_original = foods[foods["food_key"] == key]
    if len(exact_original):
        return exact_original.iloc[0], "exact"
    contains = foods[foods["food_key"].str.contains(key, regex=False, na=False)]
    if len(contains):
        return contains.iloc[0], "fuzzy"
    return None, "unmatched"


meal_text = manual_ingredients.strip()
if not meal_text and ai_food:
    meal_text = ai_food

local_rows = []
match_types = []
unmatched = []
if meal_text:
    items = [x.strip() for x in meal_text.replace("\n", ",").split(",") if x.strip()]
    for item in items:
        row, match_type = find_local_food(item)
        if row is not None:
            local_rows.append(row)
            match_types.append(match_type)
        else:
            unmatched.append(item)

usda_results = []
if unmatched:
    with st.spinner("🌎 Checking broader nutrition data..."):
        for item in unmatched:
            result = search_usda_food(item)
            if result:
                usda_results.append(result)

if meal_text:
    st.caption(f"✍️ Meal context: **{meal_text}**")

st.markdown("### ⚖️ Serving Size / Portion Adjustment")
serving_mode = st.radio("Choose portion size", ["100 g", "150 g", "200 g", "Custom"], horizontal=True)
if serving_mode == "Custom":
    serving_grams = st.number_input("Custom serving (grams)", min_value=1.0, max_value=2000.0, value=100.0, step=10.0)
else:
    serving_grams = float(serving_mode.split()[0])
st.caption(f"Nutrition values are scaled to approximately **{serving_grams:.0f} g** for each matched local food record. Actual nutrition varies by food, preparation and portion measurement.")

st.markdown("### 🔍 Ready to Analyze?")
st.caption("Add a meal above, choose a serving size, then generate its nutrition analysis.")
if "analysis_requested" not in st.session_state:
    st.session_state.analysis_requested = False

if st.button("🔍 Generate Nutrition Analysis", type="primary", use_container_width=True):
    if meal_text or uploaded_image is not None:
        st.session_state.analysis_requested = True
    else:
        st.session_state.analysis_requested = False
        st.warning("📷 Upload a meal photo or ✍️ enter at least one ingredient first.")

st.divider()
st.markdown("## 🍽️ Nutrition Analysis")
if st.session_state.analysis_requested and (meal_text or uploaded_image is not None):
    if local_rows or usda_results:
        scaled_rows = [scale_nutrition(row.to_dict(), serving_grams) for row in local_rows]
        local_calories = sum(r["Calories"] for r in scaled_rows)
        local_carbs = sum(r["Carbs"] for r in scaled_rows)
        local_protein = sum(r["Protein"] for r in scaled_rows)
        local_fat = sum(r["Fat"] for r in scaled_rows)
        local_fiber = sum(r["Fiber"] for r in scaled_rows)
        usda_calories = sum(float(r["calories"]) for r in usda_results if r.get("calories") is not None)
        usda_carbs = sum(float(r["carbs"]) for r in usda_results if r.get("carbs") is not None)
        usda_protein = sum(float(r["protein"]) for r in usda_results if r.get("protein") is not None)
        usda_fat = sum(float(r["fat"]) for r in usda_results if r.get("fat") is not None)
        calories = local_calories + usda_calories
        carbs = local_carbs + usda_carbs
        protein = local_protein + usda_protein
        fat = local_fat + usda_fat
        fiber = local_fiber

        with st.container(border=True):
            a, b, c, d, e = st.columns(5)
            a.metric("Calories", f"{calories:.0f} kcal" if calories else "N/A")
            b.metric("Carbohydrates", f"{carbs:.1f} g" if carbs else "N/A")
            c.metric("Protein", f"{protein:.1f} g" if protein else "N/A")
            d.metric("Fat", f"{fat:.1f} g" if fat else "N/A")
            e.metric("Fiber", f"{fiber:.1f} g" if fiber else "N/A")
            if local_rows:
                gl = sum(r["GL"] for r in scaled_rows)
                if not gl:
                    gl = sum(r["GI"] * r["Carbs"] / 100 for r in scaled_rows)
                st.metric("Estimated Glycemic Load", f"{gl:.1f}" if gl else "N/A")
                st.caption("GI/GL values are estimates from the project's nutrition records, not individual glucose predictions.")
            if local_rows:
                matched_names = ", ".join(str(r["English"]) for r in local_rows)
                st.success(f"✓ Local nutrition match: **{matched_names}**")
            if usda_results:
                st.caption("🌎 Additional nutrition records were matched through USDA FoodData Central.")

        st.markdown("### 📊 Model Evaluation")
        ev1, ev2, ev3, ev4 = st.columns(4)
        ev1.metric("Food-101 Classes", "101")
        ev2.metric("Recognition Confidence", f"{ai_confidence:.1f}%" if ai_confidence is not None else "Manual input")
        ev3.metric("Items Matched", str(len(local_rows) + len(usda_results)))
        exact_count = match_types.count("exact")
        alias_count = match_types.count("alias")
        local_total = len(match_types)
        ev4.metric("Local Exact/Alias", f"{exact_count + alias_count}/{local_total}" if local_total else "N/A")
        st.caption("Top-1/Top-5 accuracy and nutrition matching rates require a labelled benchmark. They are not inferred from one prediction. See MODEL_EVALUATION.md for the evaluation protocol.")
        if recognition:
            st.write("**Top predictions for this image:**")
            pred_df = pd.DataFrame([
                {"Rank": i, "Food": p.get("display_label", str(p["label"]).replace("_", " ").title()), "Confidence": f"{p['score'] * 100:.2f}%"}
                for i, p in enumerate(recognition["predictions"], 1)
            ])
            st.dataframe(pred_df, hide_index=True, use_container_width=True)

        st.markdown("### 🔗 End-to-End Pipeline")
        st.code("Image → Food Recognition → Food Name Normalization → Nutrition Database → Nutrition Analysis → Risk-Aware Educational Guidance", language="text")

        st.markdown("### 🎯 Personalized Educational Focus")
        st.write(risk_context["focus"])
        if risk_label == "ELEVATED":
            st.warning("🔎 Elevated-profile review: pay extra attention to added sugars, refined carbohydrates, fiber and portion balance.")
        elif risk_label == "MODERATE":
            st.info("🔎 Moderate-profile review: consider fiber, protein, portion balance and carbohydrate quality.")
        else:
            st.success("🔎 Baseline review: aim for a balanced meal with vegetables, fiber and adequate protein.")

        if local_rows:
            st.markdown("### 🔄 Healthier Swap Suggestions")
            swaps = []
            for row in local_rows:
                swap = str(row.get("HealthySwap", "")).strip()
                if swap and swap.lower() != "nan":
                    swaps.append(f"- **{row['English']} → {swap}** — {row.get('Why', '')}")
            if swaps:
                st.markdown("\n".join(dict.fromkeys(swaps)))
            else:
                st.caption("No verified swap is stored for the matched food record.")
    else:
        st.info("📝 The meal was received, but no verified nutrition record was found. Try a more specific food name or verify the image result.")
else:
    st.info("👆 Add a meal and click **🔍 Generate Nutrition Analysis** to see the results here.")

st.markdown("---")
st.caption("NutriGuard AI is an educational research tool. It does not diagnose diabetes or predict an individual's post-meal glucose response.")
