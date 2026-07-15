# 🥗 NutriGuard AI: Educational Nutrition Analysis for Diabetes Management

> AI-powered educational nutrition analysis tool for Indian and Korean meals using computer vision and public nutrition databases.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-Live-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## 🌐 Live Demo

**Streamlit App**

https://indo-korean-diabetes-meal-ai-ekdguqlhsxsjnhsmeszucr.streamlit.app/

---

## 📖 Overview

NutriGuard AI is an educational Digital Health application that helps users better understand the nutritional characteristics of everyday meals.

Users upload a food image, and the application estimates:

- 🍚 Food identification
- 🥗 Nutritional composition
- 📊 Estimated Glycemic Index (GI)
- 📈 Estimated Glycemic Load (GL)
- 💡 Healthier meal alternatives

The project focuses on Indian and Korean cuisines while supporting many commonly recognized foods.

---

## 🎯 Project Objectives

- Promote nutrition literacy for diabetes awareness
- Demonstrate practical applications of Artificial Intelligence in Medical IT
- Compare Indian and Korean dietary choices
- Encourage healthier food substitutions through explainable recommendations

---

## 🏗 System Architecture

```
Meal Photo
      │
      ▼
Food Recognition
(Open-source Vision Model)
      │
      ▼
Nutrition Database
USDA + ICMR + Korean Food DB
      │
      ▼
Nutrition Analysis
Calories
Carbohydrates
Protein
Fat
Fiber
      │
      ▼
Estimated Glycemic Impact
Low • Moderate • High
      │
      ▼
Healthy Meal Suggestions
Indian ↔ Korean Alternatives
      │
      ▼
Educational Disclaimer
```

---

## ✨ Features

### 📷 AI Food Recognition

- Upload meal photographs
- AI estimates food items present
- Supports Indian and Korean cuisine

---

### 📊 Nutrition Analysis

Displays estimated

- Calories
- Carbohydrates
- Protein
- Fat
- Fiber

---

### 📈 Glycemic Assessment

Displays estimated

- Glycemic Index (GI)
- Glycemic Load (GL)
- Overall Glycemic Impact

Categories

- 🟢 Low
- 🟡 Moderate
- 🔴 High

---

### 💡 Healthy Food Suggestions

Provides healthier alternatives such as

| Current Meal | Suggested Alternative |
|--------------|----------------------|
| White Rice Bibimbap | Brown Rice Bibimbap |
| Paratha | Whole Wheat Chapati |
| Cake | Fruit + Yogurt |

Each recommendation includes a short explanation.

---

### 📚 Meal History

Users can review previous analyses to observe dietary trends over time.

---

## 📸 Screenshots

### Home Page

```
Add screenshot here
```

### Nutrition Analysis

```
Add screenshot here
```

### Healthy Meal Suggestions

```
Add screenshot here
```

---

## 🛠 Technology Stack

- Python
- Streamlit
- Pandas
- Pillow
- Google Gemini Vision API
- Public Nutrition Databases

---

## 📂 Data Sources

Nutritional estimates are based on publicly available food composition resources including:

- USDA FoodData Central
- ICMR-NIN Indian Food Composition Tables
- Korean Food Composition Database

These values are intended for educational purposes and may differ from laboratory analysis.

---

## ⚠ Limitations

- Food recognition depends on image quality.
- Portion estimation is approximate.
- Nutritional values are estimated from public databases.
- Glycemic Index values vary between preparation methods.
- The application does not diagnose diabetes or provide medical treatment.

---

## 🚀 Future Improvements

- OCR for packaged food labels
- Open Food Facts integration
- Automatic portion estimation
- Expanded multilingual food database
- Improved nutrition estimation accuracy
- Evaluation with real users
- Exploration of interoperability standards such as HL7 FHIR

---

## 📦 Installation

Clone the repository

```bash
git clone https://github.com/kashish-alt0786/Indo-Korean-Diabetes-Meal-AI.git
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run locally

```bash
streamlit run app.py
```

---

## 📁 Project Structure

```
NutriGuard-AI/
│
├── app.py
├── requirements.txt
├── nutrition_database.csv
├── screenshots/
├── assets/
├── README.md
└── LICENSE
```

---

## 🎓 Educational Purpose

NutriGuard AI was developed as an educational Medical IT project to demonstrate how Artificial Intelligence, nutrition databases, and healthcare informatics can be combined into an interactive digital health application.

This project forms part of my Medical IT portfolio for undergraduate studies.

---

## 👩‍💻 Author

**Kashish**

Medical IT & Healthcare AI Enthusiast

GitHub:
https://github.com/kashish-alt0786

---

## 📄 License

Released under the MIT License.

---

## ⚕ Disclaimer

This application is intended solely for educational and informational purposes.

It is **not** a medical device and **must not** be used for diagnosis, treatment, insulin dosing, or medical decision-making. Users should consult qualified healthcare professionals for personalized medical advice.
