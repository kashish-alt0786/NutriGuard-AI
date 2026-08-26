import streamlit as st
import pandas as pd

from translations import TEXT
from food_recognition import recognize_food
from src.risk_context import build_nutrition_context, sanitize_risk
from src.usda_nutrition import search_usda_food

st.set_page_config(page_title="NutriGuard AI", page_icon="🥗", layout="wide")
foods = pd.read_csv("foods.csv")

st.info("ℹ️ **Educational research tool:** NutriGuard AI provides general nutrition information and is not a medical diagnostic or treatment tool.")

# Secure risk bridge from the diabetes-risk predictor.
query = st.query_params
risk_from_predictor = None
risk_source = None
if "risk" in query:
    raw_risk = query.get("risk")
    risk_from_predictor = sanitize_risk(raw_risk, default=0.0)
    risk_source = str(query.get("source", "")).strip()
    raw_as_text = str(raw_risk).strip()
    valid_raw = raw_as_text in {str(risk_from_predictor), f"{risk_from_predictor:.1f}", f"{risk_from_predictor:.2f}"}
    if not valid_raw and risk_from_predictor == 0.0:
        st.warning("⚠️ The received risk value was invalid or outside 0–100%. A safe default of 0% was used.")

with st.sidebar:
    st.markdown("## 🥗 NutriGuard AI")
    language = "English"
    t = TEXT[language]
    st.divider()

st.title("🥗 NutriGuard AI")
st.subheader("Risk-Aware Nutrition Intelligence")
st.caption("Understand your food. Make informed choices.")

# ── Module 1: Risk profile ──────────────────────────────────────────────────
st.divider()
st.header("🩺 1. My Risk Profile")

if "risk_profile" not in st.session_state:
    st.session_state.risk_profile = risk_from_predictor if risk_from_predictor is not None else 50.0

if risk_from_predictor is not None:
    connected_label = "Low" if risk_from_predictor < 30 else "Moderate" if risk_from_predictor < 60 else "Elevated"
    source_text = " from the Diabetes Risk Predictor" if risk_source == "diabetes-risk-predictor" else " through the risk handoff"
    st.info(f"ℹ️ **Integration Active:** Successfully ingested a statistical model risk vector of **{risk_from_predictor:.1f}%**{source_text}.")
    st.success(f"🔗 **Connected risk: {risk_from_predictor:.1f}% — {connected_label.upper()}**")
    st.caption("The received value is validated before it is used to tailor educational nutrition emphasis.")
    use_connected = st.radio("Use the connected result?", ["Yes — use my predictor result", "No — enter another estimate"], horizontal=True)
else:
    use_connected = "No — enter another estimate"

if risk_from_predictor is not None and use_connected.startswith("Yes"):
    risk_percentage = risk_from_predictor
    st.session_state.risk_profile = risk_percentage
else:
    risk_percentage = st.slider("Estimated diabetes risk (%)", 0, 100, int(round(st.session_state.risk_profile)), 1)
    st.session_state.risk_profile = float(risk_percentage)

context = build_nutrition_context(risk_percentage)
risk_label = context["label"].upper()
risk_icon = "🟢" if risk_label == "LOW" else "🟡" if risk_label == "MODERATE" else "🔴"
st.metric("Estimated Risk Profile", f"{risk_percentage:.0f}%", f"{risk_icon} {risk_label}")
st.caption("The risk profile is used only to tailor educational nutrition emphasis; it is not a diagnosis.")

# ── Module 2: meal input ────────────────────────────────────────────────────
st.divider()
st.header("🥗 2. My Meal")
st.write("Upload a meal photo, enter ingredients manually, or use both. The app checks its local nutrition database first and can use USDA FoodData Central as a broader nutrition fallback.")

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
usda_food = None
if uploaded_image is not None:
    from PIL import Image
    image = Image.open(uploaded_image).convert("RGB")
    st.image(image, caption="Uploaded meal image", use_container_width=True)
    with st.spinner("🤖 Analyzing food image..."):
        recognition = recognize_food(image, top_k=5)
    ai_food = recognition["food"]
    ai_confidence = float(recognition["confidence"])
    st.success(f"🍽️ Detected Food: **{ai_food}**")
    st.metric("🎯 Recognition Confidence", f"{ai_confidence:.2f}%")
    with st.expander("🔎 View Top Predictions"):
        for i, p in enumerate(recognition["predictions"], 1):
            st.write(f"{i}. **{p['label'].replace('_', ' ').title()}** — {p['score'] * 100:.2f}%")

# All foods are treated as one collection. Local data is preferred; USDA is a fallback.
foods["food_key"] = foods["English"].astype(str).str.strip().str.lower()
selected_food = None
selected_row = None

if ai_food:
    match = foods[foods["food_key"] == ai_food.strip().lower()]
    if len(match):
        selected_food = match.iloc[0]["English"]
        selected_row = match.iloc[0]
    else:
        # Broader nutrition lookup for foods outside the project's local CSV.
        with st.spinner("🌎 Looking for broader nutrition data..."):
            usda_food = search_usda_food(ai_food)
        if usda_food:
            st.success(f"🌎 Nutrition match found: **{usda_food['name']}**")
            st.caption("Nutrition source: USDA FoodData Central.")
        else:
            st.warning("⚠️ The image model recognized a food that is not yet matched to the local database or available USDA lookup. Please verify or enter the food name manually.")

if ai_confidence is not None and ai_confidence < 70:
    st.warning(f"⚠️ Image recognition confidence is {ai_confidence:.2f}%. Please verify the detected food before using the nutrition information.")

if manual_ingredients.strip():
    st.caption(f"✍️ Manual meal context: **{manual_ingredients}**")
if selected_food is None and usda_food is None and not manual_ingredients.strip():
    st.info("📷 Upload a meal or ✍️ enter ingredients to continue.")

# ── Transparent system handshake ───────────────────────────────────────────
st.divider()
st.subheader("🧠 NutriGuard Decision Context")
st.info(f"ℹ️ **System Core:** {context['logic_trace']}")
st.caption("This is an educational nutrition layer. It does not diagnose disease or predict an individual's post-meal glucose response.")

meal_context = manual_ingredients.strip() if manual_ingredients.strip() else (selected_food or ai_food or "")
context = build_nutrition_context(risk_percentage, meal_context)

if meal_context:
    st.markdown("### 🎯 Educational Nutrition Focus")
    st.write(context["focus"])

    if selected_row is not None:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Calories", f"{selected_row['Calories']} kcal")
        c2.metric("Carbohydrates", f"{selected_row['Carbs']} g")
        c3.metric("Protein", f"{selected_row['Protein']} g")
        c4.metric("Fat", f"{selected_row['Fat']} g")

        if "GI" in selected_row.index:
            gi = float(selected_row["GI"])
            carbs = float(selected_row["Carbs"])
            gl = (gi * carbs) / 100.0
            st.metric("Estimated Glycemic Load", f"{gl:.1f}")
            st.caption("GI/GL values are estimates from the project's nutrition database and should not be interpreted as individual glucose predictions.")

    elif usda_food is not None:
        c1, c2, c3, c4 = st.columns(4)
        calories = usda_food.get("calories")
        carbs = usda_food.get("carbs")
        protein = usda_food.get("protein")
        fat = usda_food.get("fat")
        c1.metric("Calories", f"{float(calories):.0f} kcal" if calories is not None else "N/A")
        c2.metric("Carbohydrates", f"{float(carbs):.1f} g" if carbs is not None else "N/A")
        c3.metric("Protein", f"{float(protein):.1f} g" if protein is not None else "N/A")
        c4.metric("Fat", f"{float(fat):.1f} g" if fat is not None else "N/A")
        st.caption("USDA values are database values for the matched food record; actual nutrition varies with recipe, portion and preparation.")

    if risk_label == "ELEVATED":
        st.warning("🔎 Elevated-profile review: pay particular attention to added sugars, highly refined carbohydrates, fiber and portion size.")
    elif risk_label == "MODERATE":
        st.info("🔎 Moderate-profile review: consider fiber, protein, portion balance and carbohydrate quality when evaluating this meal.")
    else:
        st.success("🔎 Baseline review: focus on a balanced meal containing vegetables, fiber and adequate protein.")

st.markdown("---")
st.subheader("📌 About the Risk Handoff")
st.caption("The diabetes-risk application passes a statistical model output through a URL parameter. NutriGuard validates that value before applying its educational rules. The handoff does not establish a medical diagnosis or causal relationship between a meal and diabetes risk.")
