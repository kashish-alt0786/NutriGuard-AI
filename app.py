import streamlit as st
import pandas as pd
import plotly.express as px
from urllib.parse import urlparse, parse_qs
from translations import TEXT
from food_recognition import recognize_food

st.set_page_config(page_title="NutriGuard AI", page_icon="🥗", layout="wide")
foods = pd.read_csv("foods.csv")

# Small notice at the top; no large disclaimer footer.
st.info("ℹ️ **Educational research tool:** NutriGuard AI provides general nutrition information and is not a medical diagnostic or treatment tool.")

# ── Risk bridge ─────────────────────────────────────────────────────────────
# The diabetes-risk project links here with ?risk=<model result>.
query = st.query_params
risk_from_predictor = None
try:
    if "risk" in query:
        raw_risk = query.get("risk")
        if raw_risk is not None:
            risk_from_predictor = max(0.0, min(100.0, float(raw_risk)))
except (TypeError, ValueError):
    risk_from_predictor = None

with st.sidebar:
    st.markdown("## 🥗 NutriGuard AI")
    language = st.selectbox("🌐 Language", ["English", "한국어"])
    t = TEXT[language]
    st.divider()
    category = st.selectbox("📂 Food Category", ["All", "Indian Home", "Indian Street", "Korean Home", "Korean Street", "International"])

if category != "All":
    foods = foods[foods["Category"] == category]

st.title("🥗 NutriGuard AI")
st.subheader("Risk-Aware Nutrition Intelligence")
st.caption("Understand your food. Make informed choices.")

# ── Module 1: Risk profile ──────────────────────────────────────────────────
st.divider()
st.header("🩺 1. My Risk Profile")

if risk_from_predictor is not None:
    risk_percentage = risk_from_predictor
    if risk_percentage < 30:
        risk_label, risk_icon = "LOW", "🟢"
    elif risk_percentage < 60:
        risk_label, risk_icon = "MODERATE", "🟡"
    else:
        risk_label, risk_icon = "ELEVATED", "🔴"
    st.success(f"🔗 **Risk received from Diabetes Risk Predictor: {risk_percentage:.1f}% — {risk_label}**")
    st.caption("Your actual model result was transferred automatically. You can still choose a different educational risk profile below.")
    use_connected = st.radio("Use the connected result?", ["Yes — use my predictor result", "No — enter another estimate"], horizontal=True)
else:
    use_connected = "No — enter another estimate"

if risk_from_predictor is not None and use_connected.startswith("Yes"):
    risk_percentage = risk_from_predictor
else:
    risk_percentage = st.slider("Estimated diabetes risk (%)", 0, 100, int(round(risk_from_predictor or 50)), 1)

if risk_percentage < 30:
    risk_label, risk_icon = "LOW", "🟢"
elif risk_percentage < 60:
    risk_label, risk_icon = "MODERATE", "🟡"
else:
    risk_label, risk_icon = "ELEVATED", "🔴"

st.metric("Estimated Risk Profile", f"{risk_percentage:.0f}%", risk_label)
st.caption("The risk profile is used only to tailor educational nutrition emphasis; it is not a diagnosis.")

# ── Module 2: meal input ────────────────────────────────────────────────────
st.divider()
st.header("🥗 2. My Meal")
st.write("Upload a meal photo, enter ingredients manually, or use both. Manual input lets you correct or supplement AI recognition.")

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
    with st.spinner("🤖 Analyzing food image..."):
        recognition = recognize_food(image, top_k=5)
    ai_food = recognition["food"]
    ai_confidence = float(recognition["confidence"])
    st.success(f"🍽️ Detected Food: **{ai_food}**")
    st.metric("🎯 Recognition Confidence", f"{ai_confidence:.2f}%")
    with st.expander("🔎 View Top Predictions"):
        for i, p in enumerate(recognition["predictions"], 1):
            st.write(f"{i}. **{p['label'].replace('_', ' ').title()}** — {p['score'] * 100:.2f}%")

foods["food_key"] = foods["English"].astype(str).str.strip().str.lower()
selected_food = None
if ai_food:
    match = foods[foods["food_key"] == ai_food.strip().lower()]
    if ai_confidence >= 70 and len(match):
        selected_food = match.iloc[0]["English"]
    elif ai_confidence < 70:
        st.warning(f"⚠️ Recognition confidence is {ai_confidence:.2f}%. Please verify the result or use the manual field.")
        if recognition:
            for p in recognition["predictions"]:
                candidate = p["label"].replace("_", " ").strip().lower()
                m = foods[foods["food_key"] == candidate]
                if len(m):
                    selected_food = m.iloc[0]["English"]
                    st.info(f"Best available database match: **{selected_food}**. Please verify it.")
                    break
    else:
        st.warning(f"⚠️ **{ai_food}** was recognized, but it is not available in the nutrition database.")

if manual_ingredients.strip():
    st.caption(f"✍️ Manual meal context: **{manual_ingredients}**")
if selected_food is None and not manual_ingredients.strip():
    st.info("📷 Upload a meal or ✍️ enter ingredients to continue.")

# ── Module 3: food intelligence ────────────────────────────────────────────
st.divider()
st.header("🧠 3. Food Intelligence")
if risk_percentage < 30:
    mode = "General balanced nutrition education"
elif risk_percentage < 60:
    mode = "Higher emphasis on fiber, balanced portions, whole grains, vegetables, and limiting sugary drinks"
else:
    mode = "Elevated-risk educational guidance emphasizing fiber-rich foods, balanced portions, whole grains, vegetables, and limiting sugary drinks"
st.info(f"🧠 **NutriGuard Decision Context**  \nRisk profile: **{risk_percentage:.0f}% — {risk_label}**  \nGuidance mode: **{mode}**")

analyze = st.button("📊 Generate Food Analysis", use_container_width=True, type="primary")
if analyze:
    if selected_food is None:
        st.warning("No verified nutrition-database food match is available yet. Please upload a clearer image or enter a food that appears in the database.")
    else:
        result = foods[foods["English"] == selected_food].iloc[0]
        st.subheader(f"🍽️ {result['English']}")

        # Transparent educational scoring; not a medical score.
        fiber_score = min(float(result["Fiber"]) / 10 * 100, 100)
        protein_score = min(float(result["Protein"]) / 25 * 100, 100)
        carb_score = max(0, 100 - float(result["Carbs"]) / 80 * 100)
        nutrition_score = round(.4 * fiber_score + .35 * protein_score + .25 * carb_score)
        st.metric("📊 Educational Nutrition Score", f"{nutrition_score}/100")

        cols = st.columns(6)
        vals = [("🔥 Calories", f"{result['Calories']} kcal"), ("🍞 Carbohydrates", f"{result['Carbs']} g"), ("🥩 Protein", f"{result['Protein']} g"), ("🥑 Fat", f"{result['Fat']} g"), ("🥦 Fiber", f"{result['Fiber']} g"), ("📉 GL", str(result["GL"]))]
        for c, (label, value) in zip(cols, vals):
            c.metric(label, value)

        st.subheader("🧠 Why This Meal?")
        st.write(result["Why"])

        gl = float(result["GL"])
        impact = "🟢 LOW" if gl <= 10 else "🟡 MODERATE" if gl <= 19 else "🔴 HIGH"
        st.subheader("📈 Glycemic Impact")
        st.info(f"**{impact}** — Estimated GI: **{result['GI']}** | Estimated GL: **{result['GL']}**. These are educational estimates and actual response varies by person, portion, and preparation.")

        st.subheader("🔄 Smart Swap")
        a, b = st.columns(2)
        a.success(f"Consider: **{result['HealthySwap']}**")
        b.info(result["Why"])

        st.subheader("🍽️ Build a Better Plate")
        st.write("Example structure: more non-starchy vegetables, a fiber-rich carbohydrate source, a protein source, and a small amount of healthy fat. Individual needs vary.")
        plate = pd.DataFrame({"Component": ["Vegetables", "Fiber-rich carbohydrate", "Protein", "Healthy fat"], "Share": [40, 25, 25, 10]})
        st.plotly_chart(px.pie(plate, names="Component", values="Share", hole=.45, title="Example Balanced Plate"), use_container_width=True)

        st.subheader("🔬 Why the Risk Profile Matters")
        if risk_percentage >= 60:
            st.warning("Because the supplied risk profile is elevated, NutriGuard places greater educational emphasis on fiber-rich foods, balanced portions, and limiting sugary drinks and highly refined carbohydrates.")
        elif risk_percentage >= 30:
            st.info("Because the supplied risk profile is moderate, NutriGuard emphasizes balanced meals, fiber, vegetables, and portion awareness.")
        else:
            st.success("The supplied risk profile is low; NutriGuard uses general balanced-nutrition guidance while still highlighting the meal's nutritional characteristics.")

        st.subheader("📈 Weekly Meal Impact — Demonstration")
        history = pd.DataFrame({"Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], "Impact": ["Low", "Moderate", "High", "Low", "Moderate", "High", "Low"]})
        counts = history["Impact"].value_counts().reset_index()
        counts.columns = ["Impact", "Days"]
        st.plotly_chart(px.bar(counts, x="Impact", y="Days", text="Days", title="Example Weekly Summary"), use_container_width=True)
        st.caption("This is a demonstration visualization, not a stored patient history.")

# ── Resources ───────────────────────────────────────────────────────────────
st.divider()
st.header("📚 Educational Resources")
a, b = st.columns(2)
with a:
    st.link_button("🇺🇸 American Diabetes Association", "https://diabetes.org")
    st.link_button("🇺🇸 USDA FoodData Central", "https://fdc.nal.usda.gov")
    st.link_button("🌍 World Health Organization", "https://www.who.int")
with b:
    st.link_button("🇮🇳 ICMR – National Institute of Nutrition", "https://www.nin.res.in")
    st.link_button("🇰🇷 Korean Nutrition Society", "https://www.kns.or.kr")

st.divider()
st.caption("NutriGuard AI • Risk-aware educational nutrition intelligence • © 2026")
