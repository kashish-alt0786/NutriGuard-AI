import streamlit as st
import pandas as pd
import plotly.express as px

from translations import TEXT
from food_recognition import recognize_food

st.set_page_config(
    page_title="NutriGuard AI",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)

foods = pd.read_csv("foods.csv")

# Small, permanent notice at the top — detailed disclaimers are intentionally
# kept out of the footer to keep the interface clean.
st.info(
    "ℹ️ **Educational research tool:** NutriGuard AI provides general nutrition "
    "information and is not a medical diagnostic or treatment tool."
)

with st.sidebar:
    st.image("https://img.icons8.com/color/96/salad.png", width=70)
    language = st.selectbox("🌐 Language", ["English", "한국어"])
    t = TEXT[language]
    st.divider()
    st.markdown("## 📂 Categories")
    category = st.selectbox(
        "",
        [
            "All",
            "Indian Home",
            "Indian Street",
            "Korean Home",
            "Korean Street",
            "International",
        ],
    )

if category != "All":
    foods = foods[foods["Category"] == category]

st.title("🥗 NutriGuard AI")
st.subheader("Risk-Aware Nutrition Intelligence")
st.caption("Understand your food. Make informed choices.")

# ─────────────────────────────────────────────────────────────
# MODULE 1 — RISK PROFILE
# ─────────────────────────────────────────────────────────────
st.divider()
st.header("🩺 1. My Risk Profile")
st.write(
    "Use an estimated diabetes-risk result from the connected diabetes "
    "project, or enter your own risk percentage for educational nutrition guidance."
)

risk_mode = st.radio(
    "How would you like to provide your risk profile?",
    [
        "I already know my estimated risk",
        "I need to calculate my risk",
    ],
    horizontal=True,
)

risk_percentage = None

if risk_mode == "I already know my estimated risk":
    risk_percentage = st.slider(
        "Estimated diabetes risk (%)",
        min_value=0,
        max_value=100,
        value=50,
        step=1,
    )
else:
    st.caption(
        "Enter the core values below for an educational risk estimate. "
        "This simplified calculation is not a clinical diagnosis."
    )
    r1, r2, r3 = st.columns(3)
    with r1:
        glucose = st.number_input("Glucose (mg/dL)", 40, 300, 120)
        bmi = st.number_input("BMI", 10.0, 70.0, 25.0, step=0.1)
    with r2:
        blood_pressure = st.number_input("Blood Pressure (mmHg)", 40, 200, 70)
        age = st.number_input("Age", 18, 100, 30)
    with r3:
        pregnancies = st.number_input("Pregnancies", 0, 20, 0)

    if st.button("🩺 Calculate Estimated Risk", use_container_width=True):
        # Transparent educational heuristic rather than pretending to run a
        # clinical model that is not exposed by this nutrition repository.
        glucose_component = max(0.0, min(100.0, (glucose - 70) / 130 * 100))
        bmi_component = max(0.0, min(100.0, (bmi - 18.5) / 31.5 * 100))
        age_component = max(0.0, min(100.0, (age - 18) / 62 * 100))
        bp_component = max(0.0, min(100.0, (blood_pressure - 60) / 100 * 100))
        pregnancy_component = min(100.0, pregnancies / 10 * 100)
        risk_percentage = round(
            0.45 * glucose_component
            + 0.20 * bmi_component
            + 0.15 * age_component
            + 0.10 * bp_component
            + 0.10 * pregnancy_component,
            1,
        )
        st.session_state["calculated_risk"] = risk_percentage

if risk_percentage is None and "calculated_risk" in st.session_state:
    risk_percentage = st.session_state["calculated_risk"]

if risk_percentage is not None:
    if risk_percentage < 30:
        risk_label = "LOW"
        risk_icon = "🟢"
    elif risk_percentage < 60:
        risk_label = "MODERATE"
        risk_icon = "🟡"
    else:
        risk_label = "ELEVATED"
        risk_icon = "🔴"

    st.success(
        f"{risk_icon} **Estimated risk profile: {risk_percentage:.0f}% — {risk_label}**"
    )
    st.caption(
        "This is an estimated risk profile used only to adjust educational nutrition emphasis."
    )

# ─────────────────────────────────────────────────────────────
# MODULE 2 — MEAL INPUT
# ─────────────────────────────────────────────────────────────
st.divider()
st.header("🥗 2. My Meal")
st.write(
    "Upload a meal photo, enter ingredients manually, or use both. "
    "Manual input lets you correct or supplement AI recognition."
)

meal_col, manual_col = st.columns(2)

with meal_col:
    st.subheader("📷 Upload Your Meal")
    uploaded_image = st.file_uploader(
        "Upload meal image",
        type=["jpg", "jpeg", "png"],
        help="For best results, use a clear image containing one main meal or food.",
    )

with manual_col:
    st.subheader("✍️ Describe Your Meal")
    manual_ingredients = st.text_area(
        "Enter or edit ingredients",
        placeholder="Example: rice, grilled chicken, broccoli",
        height=150,
    )

ai_food = None
ai_confidence = None
recognition = None

if uploaded_image is not None:
    from PIL import Image

    image = Image.open(uploaded_image).convert("RGB")
    st.image(image, caption="Uploaded meal image", use_container_width=True)

    with st.spinner("🤖 Analyzing food image..."):
        recognition = recognize_food(image, top_k=5)

    ai_food = recognition["food"]
    ai_confidence = recognition["confidence"]

    st.success(f"🍽️ Detected Food: **{ai_food}**")
    st.metric("🎯 Model Confidence", f"{ai_confidence:.2f}%")

    with st.expander("🔎 View Top Predictions"):
        for i, prediction in enumerate(recognition["predictions"], start=1):
            label = prediction["label"].replace("_", " ").title()
            score = prediction["score"] * 100
            st.write(f"{i}. **{label}** — {score:.2f}%")

CONFIDENCE_THRESHOLD = 70.0
foods["food_key"] = foods["English"].astype(str).str.strip().str.lower()
selected_food = None

if ai_food is not None:
    ai_key = ai_food.strip().lower()
    ai_match = foods[foods["food_key"] == ai_key]

    if ai_confidence >= CONFIDENCE_THRESHOLD and len(ai_match) > 0:
        selected_food = ai_match.iloc[0]["English"]
    elif ai_confidence >= CONFIDENCE_THRESHOLD:
        st.warning(
            f"⚠️ **{ai_food}** was recognized with {ai_confidence:.2f}% confidence, "
            "but it is not available in the nutrition database."
        )
    else:
        st.warning(
            f"⚠️ Recognition confidence is only {ai_confidence:.2f}%. "
            "Please verify the food or use the manual ingredient field."
        )
        if recognition is not None:
            for prediction in recognition["predictions"]:
                candidate = (
                    prediction["label"].replace("_", " ").strip().lower()
                )
                candidate_match = foods[foods["food_key"] == candidate]
                if len(candidate_match) > 0:
                    selected_food = candidate_match.iloc[0]["English"]
                    st.info(
                        f"ℹ️ Best available database match: **{selected_food}**. "
                        "Verify the identification before interpreting these educational values."
                    )
                    break

if selected_food is None and manual_ingredients.strip():
    # A manual ingredient list does not force an invented database match.
    # It is retained as context and shown in the analysis summary below.
    st.info("✍️ Manual ingredients received. They will be included as meal context.")

if selected_food is None and not manual_ingredients.strip():
    st.info("📷 Upload a meal or ✍️ enter ingredients to continue.")

# ─────────────────────────────────────────────────────────────
# MODULE 3 — FOOD INTELLIGENCE
# ─────────────────────────────────────────────────────────────
st.divider()
st.header("🧠 3. Food Intelligence")

if risk_percentage is not None:
    guidance_mode = (
        "General balanced nutrition education"
        if risk_percentage < 30
        else "Higher emphasis on fiber, balanced portions, whole grains, vegetables, and limiting sugary drinks"
        if risk_percentage < 60
        else "Elevated-risk educational guidance emphasizing fiber-rich foods, balanced portions, whole grains, vegetables, and limiting sugary drinks"
    )
    st.info(
        f"🧠 **NutriGuard Decision Context**  \n"
        f"Risk profile: **{risk_percentage:.0f}% — {risk_label}**  \n"
        f"Guidance mode: **{guidance_mode}**"
    )
else:
    st.info(
        "🧠 **NutriGuard Decision Context**  \n"
        "No risk profile supplied. General nutrition education will be used."
    )

analyze = st.button(
    "📊 Generate Food Analysis",
    use_container_width=True,
    type="primary",
)

if analyze:
    if selected_food is None:
        st.warning(
            "Please provide a food database match or upload a recognizable meal image. "
            "Manual ingredients are retained as context but do not invent nutrition values."
        )
    else:
        result = foods[foods["English"] == selected_food].iloc[0]

        st.subheader(f"🍽️ {result['English']}")
        if manual_ingredients.strip():
            st.caption(f"Manual meal context: {manual_ingredients}")

        st.subheader("📊 Educational Nutrition Score")
        fiber_score = min(float(result["Fiber"]) / 10 * 100, 100)
        protein_score = min(float(result["Protein"]) / 25 * 100, 100)
        carb_score = max(0, 100 - float(result["Carbs"]) / 80 * 100)
        nutrition_score = round(
            0.4 * fiber_score + 0.35 * protein_score + 0.25 * carb_score
        )
        st.metric("Nutrition Score", f"{nutrition_score}/100")

        metrics = st.columns(6)
        values = [
            ("🔥 Calories", f"{result['Calories']} kcal"),
            ("🍞 Carbohydrates", f"{result['Carbs']} g"),
            ("🥩 Protein", f"{result['Protein']} g"),
            ("🥑 Fat", f"{result['Fat']} g"),
            ("🥦 Fiber", f"{result['Fiber']} g"),
            ("📉 GL", str(result["GL"])),
        ]
        for column, (label, value) in zip(metrics, values):
            with column:
                st.metric(label, value)

        st.subheader("🧠 Why This Meal?")
        st.write(result["Why"])

        st.subheader("📈 Glycemic Impact")
        gl = float(result["GL"])
        if gl <= 10:
            impact = "🟢 LOW"
            message = "This food has a relatively low estimated glycemic load."
        elif gl <= 19:
            impact = "🟡 MODERATE"
            message = "This food has a moderate estimated glycemic load."
        else:
            impact = "🔴 HIGH"
            message = "This food has a relatively high estimated glycemic load."

        st.info(
            f"**{impact}** — {message} Estimated GI: **{result['GI']}** | "
            f"Estimated GL: **{result['GL']}**"
        )

        st.subheader("🔄 Smart Swap")
        swap_col, why_col = st.columns(2)
        with swap_col:
            st.success(f"Consider: **{result['HealthySwap']}**")
        with why_col:
            st.info(result["Why"])

        st.subheader("🍽️ Build a Better Plate")
        st.write(
            "A balanced plate can include a generous vegetable component, a "
            "fiber-rich carbohydrate source, and a protein source. Adjust portions "
            "to your needs and consult a qualified professional for individualized advice."
        )
        plate = pd.DataFrame(
            {
                "Component": ["Vegetables", "Fiber-rich carbohydrate", "Protein", "Healthy fat"],
                "Share": [40, 25, 25, 10],
            }
        )
        fig = px.pie(plate, names="Component", values="Share", hole=0.45)
        fig.update_layout(title="Example Balanced Plate")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📈 Meal History Demonstration")
        history = pd.DataFrame(
            {
                "Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                "Glycemic Impact": ["Low", "Moderate", "High", "Low", "Moderate", "High", "Low"],
            }
        )
        impact_count = history["Glycemic Impact"].value_counts().reset_index()
        impact_count.columns = ["Impact", "Days"]
        fig = px.bar(
            impact_count,
            x="Impact",
            y="Days",
            text="Days",
            title="Weekly Glycemic Impact Summary",
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Meal history is currently a demonstration feature and is not a persistent patient record.")

# ─────────────────────────────────────────────────────────────
# RESOURCES
# ─────────────────────────────────────────────────────────────
st.divider()
st.header("📚 Educational Resources")
st.write(
    "Explore evidence-based nutrition and diabetes information from trusted organizations."
)

col1, col2 = st.columns(2)
with col1:
    st.link_button("🇺🇸 American Diabetes Association", "https://diabetes.org")
    st.link_button("🇺🇸 USDA FoodData Central", "https://fdc.nal.usda.gov")
    st.link_button("🌍 World Health Organization", "https://www.who.int")
with col2:
    st.link_button("🇮🇳 ICMR – National Institute of Nutrition", "https://www.nin.res.in")
    st.link_button("🇰🇷 Korean Nutrition Society", "https://www.kns.or.kr")

st.divider()
st.caption(
    "NutriGuard AI • Educational nutrition intelligence • © 2026 NutriGuard AI"
)
