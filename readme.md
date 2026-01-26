# ShieldMail – AI-Powered Scam Detection Platform

**TechRush Hackathon Project**

ShieldMail is an AI-powered web application designed to help students and professionals
identify fake job and internship emails. It analyzes email content using Machine Learning,
rule-based red flag detection, and optional AI-generated explanations.

---

## 🚨 Problem Statement
Online job and internship scams are increasing rapidly. These scams often look professional,
making them hard to detect. Victims may lose money or sensitive personal data.

---

## 💡 Solution
ShieldMail allows users to:
- Paste suspicious email content
- Analyze scam probability using NLP & ML
- Detect red flags like fees, urgency, and payment requests
- Get a clear risk verdict: **Safe / Suspicious / High Risk**
- View visual risk breakdown using charts

---

## 🧠 How It Works
1. Email text is cleaned and preprocessed
2. ML model predicts scam probability
3. Rule-based checks detect red flags
4. Final risk score and explanation are generated
5. Results are visualized using charts

---

## 🛠 Tech Stack
- **Backend:** Python, Flask
- **ML/NLP:** Scikit-learn
- **Database:** MySQL (Railway)
- **Frontend:** HTML, CSS, JavaScript
- **Visualization:** Google Charts
- **AI Explanation:** Gemini API 

## 🛠 Deployment

This project is deployed using **Render**.

- Backend: Flask + Gunicorn
- Hosting Platform: Render
- Model: Pre-trained ML model loaded at runtime
- Database: Optional (disabled for demo reliability)

Render was chosen for its stability with Python-based ML applications and server-side execution.
---

## 🚀 Live Demo

[![Deployed on Render](https://img.shields.io/badge/Deployed%20on-Render-46E3B7?logo=render&logoColor=white)](https://shieldmail.onrender.com)
Note: Render takes some time to load due to free tier limit.

## 👥 Team
**Team Name:** LazyCoders  
**Hackathon:** TechRush  
**Team Members:** Siddharth and Saish

---

## ⚠️ Disclaimer

ShieldMail is an AI-assisted scam detection tool designed to help users assess the risk of suspicious emails and job or internship offers.  
The analysis is based on machine learning models and heuristic indicators, which may occasionally produce false positives or false negatives.

ShieldMail should not be considered a substitute for professional verification or legal advice.  
Users are encouraged to exercise personal judgment and verify critical information through official channels before taking action.
