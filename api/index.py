print(">>> ACTIVE app.py <<<")

import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify, render_template
import pickle
import re

from pipeline import clean_text
from database import get_connection
from gemini_helper import rewrite_explanation

app = Flask(__name__)

# -----------------------------------
# Load ML model and vectorizer
# -----------------------------------
MODEL_PATH = os.path.join(os.path.dirname(__file__), "scam_model.pkl")
VECTORIZER_PATH = os.path.join(os.path.dirname(__file__), "vectorizer.pkl")

with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

with open(VECTORIZER_PATH, "rb") as f:
    vectorizer = pickle.load(f)

# -----------------------------------
# Frontend route
# -----------------------------------
@app.route("/")
def home():
    return render_template("index.html")

# -----------------------------------
# Red flag extraction
# -----------------------------------
def extract_red_flags(text):
    t = text.lower()
    flags = []

    # Fee detection (safe)
    if re.search(r"\bfee\b", t) and not re.search(
        r"\b(no|without)\s+(any\s+)?(registration\s+)?fee\b", t
    ):
        flags.append("Upfront fee requested")

    # Payment methods
    if any(x in t for x in ["upi", "wallet", "gift card", "crypto"]):
        flags.append("Unusual payment method requested")

    # Urgency
    if any(x in t for x in [
        "urgent", "immediately", "within 24 hours",
        "pay now", "final notice", "action required"
    ]):
        flags.append("Urgent pressure tactics")

    return flags

# -----------------------------------
# Analysis API
# -----------------------------------
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(force=True)
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"error": "Empty input"}), 400

    # -------- ML prediction --------
    cleaned = clean_text(text)
    vec = vectorizer.transform([cleaned])
    ml_prob = float(model.predict_proba(vec)[0][1])

    # -------- Rule-based signals --------
    red_flags = extract_red_flags(text)

    # -------- Final score --------
    final_score = (ml_prob * 100) + (len(red_flags) * 20)
    final_score = min(final_score, 100)

    # -------- Final label --------
    if final_score >= 70:
        final_label = "High Risk"
    elif final_score >= 35:
        final_label = "Suspicious"
    else:
        final_label = "Safe"

    # -------- Explanation (FIXED) --------
    if final_label == "Safe":
        base_explanation = (
            "This email appears safe. No strong scam indicators such as payment "
            "requests, suspicious wording, or urgency were detected."
        )

    elif final_label == "Suspicious":
        if red_flags:
            base_explanation = (
                "This email shows warning signs such as "
                + ", ".join(red_flags)
                + ". It should be reviewed carefully before proceeding."
            )
        else:
            base_explanation = (
                "This email shows behavioral patterns commonly associated with scams, "
                "such as vague intent, indirect requests, or abnormal phrasing. "
                "While no explicit red flags were detected, caution is advised."
            )

    else:  # High Risk
        if red_flags:
            base_explanation = (
                "This email shows strong scam indicators including "
                + ", ".join(red_flags)
                + ". It poses a high risk and should be avoided."
            )
        else:
            base_explanation = (
                "This email exhibits strong scam-like behavior based on language intent "
                "and classification confidence, even without explicit red flags."
            )

    # -------- Gemini rewrite (optional) --------
    ai_explanation = rewrite_explanation(base_explanation)
    final_explanation = ai_explanation if ai_explanation else base_explanation

    # -------- Store result (non-blocking) --------
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO analysis_logs
            (input_text, ml_probability, final_score, final_label)
            VALUES (%s, %s, %s, %s)
            """,
            (text, ml_prob, final_score, final_label)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print("DB error:", e)

    # -------- Response --------
    return jsonify({
        "final_label": final_label,
        "ml_probability": ml_prob,
        "final_score": final_score,
        "red_flags": red_flags,
        "explanation": final_explanation
    })