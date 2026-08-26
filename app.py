import streamlit as st
import pandas as pd
import plotly.express as px

from translations import TEXT
from food_recognition import recognize_food
from src.risk_context import build_nutrition_context, sanitize_risk

st.set_page_config(page_title="NutriGuard AI", page_icon="🥗", layout="wide")
foods = pd.read_csv("foods.csv")

# Small, permanent notice at the top; no large disclaimer footer.
st.info("ℹ️ **Educational research tool:** NutriGuard AI provides general nutrition information and is not a medical diagnostic or treatment tool.")

# ── Secure risk bridge ─────────────────────────────────────────────────────
# The diabetes-risk project links here with ?risk=<model result>.
# Query parameters are treated as untrusted input and are strictly validated.
query = st.query_params
risk_from_predictor = None
if "risk" in query:
    risk_from_predictor = sanitize_risk(query.get("risk"), default=0.0)
    if risk_from_predictor == 0.0 and str(query.get("risk")).strip() not in {"0", "0.0", "0.00"}:
        st.warning("⚠️ The received risk value was invalid or outside 0–100%. A safe default of 0% was used.")

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

if "risk_profile" not in st.session_state:
    st.session_state.risk_profile = risk_from_predictor if risk_from_predictor is not None else 50.0

if risk_from_predictor is not None:
    connected_label = "Low" if risk_from_predictor < 30 else "Moderate" if risk_from_predictor < 60 else "Elevated"
    st.success(f"🔗 **Risk received from Diabetes Risk Predictor: {risk_from_predictor:.1f}% — {connected_label.upper()}**")
    st.caption("The actual model result was transferred automatically through a validated URL parameter.")
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

# ── Module 3: context-aware food intelligence ───────────────────────────────
st.divider()
st.header("🧠 3. Food Intelligence")
context = build_nutrition_context(risk_percentage, manual_ingredients)
st.info(
    f"ℹ️ **System Core: Risk-aware guidance activated**  \n"
    f"Profile: **{context['risk']:.1f}% — {context['label']}**  \n"
    f"Priority: **{context['priority']}**  \n"
    f"Guidance rule: {context['focus']}"
)

analyze = st.button("📊 Generate Food Analysis", use_container_width=True, type="primary")
if analyze:
    if selected_food is None:
        st.warning("No verified nutrition-database food match is available yet. Please upload a clearer image or enter a food that appears in the database.")
    else:
        result = foods[foods["English"] == selected_food].iloc[0]
        st.subheader(f"🍽️ {result['English']}")

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

        st.subheader("🔬 Logic Trace")
        st.code(context["logic_trace"], language="text")
        st.write("The meal analysis is combined with the received risk profile to prioritize educational nutrition guidance. NutriGuard currently uses deterministic rules and its nutrition database; it does not claim to use an LLM for medical decision-making.")

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
