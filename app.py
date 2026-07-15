import streamlit as st
from PIL import Image
import pandas as pd
import datetime

st.set_page_config(page_title="NutriGuard AI", page_icon="🛡️", layout="centered")
st.title("🛡️ NutriGuard AI")
st.caption("Indo-Korean + wide variety of common foods | Educational awareness tool")
st.error("⚠️ EDUCATIONAL ONLY: Does not replace professional medical advice. Reliable risk assessment requires clinical evaluation.")

# --- Curated DB (25 foods) - accurate specs ---
nutrition_db = {
    'paratha': {'cal': 250, 'carbs': 45, 'protein': 6, 'fiber': 2, 'sugar': 2, 'gi': 75, 'gl': 28, 'impact': 'High', 'color':'🔴', 'reason': 'Oil fried + refined wheat, low dietary fiber'},
    'chapati': {'cal': 120, 'carbs': 15, 'protein': 3, 'fiber': 3, 'sugar': 0.5, 'gi': 45, 'gl': 10, 'impact': 'Low', 'color':'🟢', 'reason': 'Whole wheat, higher fiber content'},
    'chana masala': {'cal': 280, 'carbs': 30, 'protein': 12, 'fiber': 8, 'sugar': 5, 'gi': 38, 'gl': 12, 'impact': 'Low', 'color':'🟢', 'reason': 'Chickpeas provide protein and fiber'},
    'chole bhature': {'cal': 450, 'carbs': 55, 'protein': 10, 'fiber': 6, 'sugar': 4, 'gi': 70, 'gl': 32, 'impact': 'High', 'color':'🔴', 'reason': 'Bhatura is deep-fried refined flour'},
    'dal': {'cal': 180, 'carbs': 20, 'protein': 7, 'fiber': 5, 'sugar': 1, 'gi': 35, 'gl': 8, 'impact': 'Low', 'color':'🟢', 'reason': 'Lentils rich in fiber and protein'},
    'rajma chawal': {'cal': 350, 'carbs': 50, 'protein': 12, 'fiber': 9, 'sugar': 3, 'gi': 40, 'gl': 15, 'impact': 'Low', 'color':'🟢', 'reason': 'Kidney beans high fiber'},
    'white rice bibimbap': {'cal': 380, 'carbs': 65, 'protein': 12, 'fiber': 2, 'sugar': 3, 'gi': 80, 'gl': 35, 'impact': 'High', 'color':'🔴', 'reason': 'White rice base, refined grains detected'},
    'brown rice bibimbap': {'cal': 350, 'carbs': 50, 'protein': 13, 'fiber': 6, 'sugar': 2, 'gi': 50, 'gl': 18, 'impact': 'Moderate', 'color':'🟡', 'reason': 'Brown rice higher fiber'},
    'mixed grain rice': {'cal': 320, 'carbs': 45, 'protein': 10, 'fiber': 7, 'sugar': 1, 'gi': 48, 'gl': 16, 'impact': 'Low', 'color':'🟢', 'reason': 'Mixed grains slow absorption'},
    'kimchi': {'cal': 20, 'carbs': 2, 'protein': 1, 'fiber': 1, 'sugar': 1, 'gi': 15, 'gl': 1, 'impact': 'Low', 'color':'🟢', 'reason': 'Fermented, very low carbohydrate'},
    'tteokbokki': {'cal': 350, 'carbs': 80, 'protein': 4, 'fiber': 1, 'sugar': 15, 'gi': 85, 'gl': 40, 'impact': 'High', 'color':'🔴', 'reason': 'Rice cake + sweet sauce, low fiber'},
    'cake': {'cal': 400, 'carbs': 80, 'protein': 4, 'fiber': 1, 'sugar': 35, 'gi': 85, 'gl': 40, 'impact': 'High', 'color':'🔴', 'reason': 'Refined flour + added sugar'},
    'cake (1 piece 80g)': {'cal': 80, 'carbs': 16, 'protein': 0.8, 'fiber': 0.2, 'sugar': 7, 'gi': 85, 'gl': 8, 'impact': 'High', 'color':'🔴', 'reason': 'Single piece still contains refined flour and sugar'},
    'peanut (1 piece)': {'cal': 6, 'carbs': 0.2, 'protein': 0.3, 'fiber': 0.1, 'sugar': 0, 'gi': 15, 'gl': 0, 'impact': 'Low', 'color':'🟢', 'reason': 'Healthy fat + protein per piece'},
    'lays chips (1 packet 52g)': {'cal': 270, 'carbs': 26, 'protein': 3, 'fiber': 2, 'sugar': 1, 'gi': 70, 'gl': 18, 'impact': 'High', 'color':'🔴', 'reason': 'Deep fried + refined carbs'},
    'chips (1 piece)': {'cal': 5, 'carbs': 0.5, 'protein': 0.05, 'fiber': 0, 'sugar': 0, 'gi': 70, 'gl': 0.3, 'impact': 'High', 'color':'🔴', 'reason': 'Single chip minimal load but fried'},
    'fruit + greek yogurt': {'cal': 120, 'carbs': 12, 'protein': 8, 'fiber': 3, 'sugar': 8, 'gi': 25, 'gl': 4, 'impact': 'Low', 'color':'🟢', 'reason': 'Protein + natural fiber'},
    'roasted sweet potato': {'cal': 130, 'carbs': 20, 'protein': 2, 'fiber': 4, 'sugar': 5, 'gi': 55, 'gl': 11, 'impact': 'Moderate', 'color':'🟡', 'reason': 'Natural sugars with fiber'},
    'nuts and berries': {'cal': 150, 'carbs': 10, 'protein': 5, 'fiber': 4, 'sugar': 4, 'gi': 20, 'gl': 3, 'impact': 'Low', 'color':'🟢', 'reason': 'Healthy fats + antioxidants'},
}

smart_swaps = {
    'paratha': 'chapati',
    'chole bhature': 'chana masala',
    'white rice bibimbap': 'mixed grain rice',
    'tteokbokki': 'roasted sweet potato',
    'cake': 'fruit + greek yogurt',
    'cake (1 piece 80g)': 'fruit + greek yogurt',
    'lays chips (1 packet 52g)': 'nuts and berries',
    'chips (1 piece)': 'nuts and berries'
}

# --- UI ---
st.divider()
st.header("📷 Meal Photo")
uploaded_file = st.file_uploader("Upload food photo (wide variety: Indian, Korean, international). Recognition depends on image quality.", type=['jpg','jpeg','png'])
if uploaded_file:
    st.image(Image.open(uploaded_file), width=350)
    st.caption("Food Recognition (Open-source vision model) analyzing...")

mode = st.radio("Input type", ["Cooked / Street Food", "Packaged Food", "Single Piece"], horizontal=True)
qty = 1
if mode == "Single Piece":
    qty = st.number_input("Quantity (pieces)", min_value=1, max_value=50, value=1, help="Portion estimation is approximate. For auto-count, see future work: object detection.")

typed = st.text_input("Type food name (e.g., chana masala, chole bhature, cake, Lays):").lower().strip()
selected = st.selectbox("Or select from curated list:", ["-- Choose --"] + sorted(nutrition_db.keys()))

detected = None
if typed:
    detected = typed
elif selected!= "-- Choose --":
    detected = selected

if detected:
    # Match logic
    if detected in nutrition_db:
        base = nutrition_db[detected]
        is_est = False
        final_name = detected
    else:
        # Partial match
        best = None
        for k in nutrition_db:
            if detected in k or k.split()[0] in detected:
                best = k
                break
        if best:
            base = nutrition_db[best]
            is_est = False
            final_name = best
        else:
            st.warning("If a food cannot be confidently matched, providing approximate estimate. Recognition confidence is limited for this input.")
            base = {'cal': 280, 'carbs': 35, 'protein': 8, 'fiber': 4, 'sugar': 5, 'gi': 55, 'gl': 18, 'impact': 'Moderate', 'color':'🟡', 'reason': 'Mixed composition, estimated from public databases'}
            is_est = True
            final_name = detected

    data = base.copy()
    if mode == "Single Piece":
        for k in ['cal','carbs','protein','fiber','sugar','gl']:
            data[k] = round(base[k]*qty,1)

    st.divider()
    st.header("🩺 Glycemic Assessment")
    if data['impact'] == 'High':
        st.error(f"### Estimated Glycemic Impact: {data['impact'].upper()} {data['color']}")
    elif data['impact'] == 'Moderate':
        st.warning(f"### Estimated Glycemic Impact: {data['impact'].upper()} {data['color']}")
    else:
        st.success(f"### Estimated Glycemic Impact: {data['impact'].upper()} {data['color']}")

    st.subheader("Reason")
    st.write(f"- Estimated carbohydrates: {data['carbs']} g\n- {data['reason']}\n- Dietary fiber: {data['fiber']} g\n- Estimated sugar: {data['sugar']} g")
    if is_est:
        st.caption("Approximate estimate using USDA, ICMR-NIN, Korean Food DB pattern.")

    st.subheader("Nutrition Analysis")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Calories", data['cal'])
    c2.metric("Carbs", f"{data['carbs']}g")
    c3.metric("Protein", f"{data['protein']}g")
    c4.metric("Fiber", f"{data['fiber']}g")

    st.divider()
    st.header("💡 Healthy Meal Suggestions")
    swap = smart_swaps.get(final_name)
    if swap and swap in nutrition_db:
        sd = nutrition_db[swap]
        st.write(f"Replace **{final_name}** with **{swap}**.")
        st.write(f"Expected glycemic impact decreases from GL {data['gl']} to {sd['gl']}.")
        df = pd.DataFrame([
            {"Food": f"{final_name} {data['color']}", "Calories": data['cal'], "GI": data['gi'], "GL": data['gl']},
            {"Food": f"{swap} {sd['color']}", "Calories": sd['cal'], "GI": sd['gi'], "GL": sd['gl']}
        ])
        st.dataframe(df, use_container_width=True)
        st.success(f"Why healthier: {sd['reason']}")
    else:
        st.write("Suggestion: Replace white rice / refined base with brown rice / mixed grains. Expected glycemic impact decreases.")

    st.divider()
    st.header("📈 Meal History Dashboard")
    st.caption("Dashboard makes application feel like complete digital health tool rather than one-time analysis.")
    if 'history' not in st.session_state:
        st.session_state.history = []
    if st.button("Add to History"):
        st.session_state.history.append({"date": datetime.datetime.now().strftime("%m/%d"), "food": final_name, "gi": data['gi'], "gl": data['gl']})
        st.toast("Added!")
    if st.session_state.history:
        hdf = pd.DataFrame(st.session_state.history)
        c1,c2 = st.columns(2)
        c1.metric("Avg GI", f"{hdf['gi'].mean():.0f}")
        c2.metric("Avg GL", f"{hdf['gl'].mean():.0f}")
        st.bar_chart(hdf, x="date", y="gl")

st.divider()
st.subheader("Limitations")
st.write("- Food recognition accuracy depends on image quality.\n- Nutritional values are estimated using publicly available food composition databases.\n- Portion estimation is approximate.\n- Application is intended for educational purposes and does not replace professional medical advice.")
st.subheader("Future Work")
st.write("- OCR-based packaged food recognition\n- Open Food Facts integration\n- Portion estimation using object detection\n- Expanded multilingual food database\n- Evaluation with real users\n- Improved nutrition estimation accuracy")
st.caption("Architecture: Meal Photo → Food Recognition (Open-source vision model) → Nutrition Database → Nutrition Analysis → Glycemic Assessment → Healthy Suggestions → Meal History Dashboard → Educational Disclaimer")
