print(">>> ACTIVE app.py <<<")

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify, render_template
import pickle
import re

from pipeline import clean_text
from database import get_connection, init_db
from gemini_helper import rewrite_explanation

#init_db()

app = Flask(__name__)

# -----------------------------------
# Load ML model and vectorizer
# -----------------------------------
with open("model/scam_model.pkl", "rb") as f:
    model = pickle.load(f)

with open("model/vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

# -----------------------------------
# Frontend route
# -----------------------------------
@app.route("/")
def home():
    return render_template("index.html")

# -----------------------------------
# Red flag extraction (email text)
# -----------------------------------
def extract_red_flags(text):
    t = text.lower()
    flags = []

    # Fee detection (safe word-boundary)
    if re.search(r"\bfee\b", t) and not re.search(
        r"\b(no|without)\s+(any\s+)?(registration\s+)?fee\b", t
    ):
        flags.append("Upfront fee requested")

    # Unusual payment methods
    if any(x in t for x in ["upi", "wallet", "gift card"]):
        flags.append("Unusual payment method requested")

    # Urgent language
    if any(x in t for x in ["pay now", "pay today", "urgent", "immediately", "within 24 hours"]):
        flags.append("Urgent payment pressure")

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

    # -------- Rule-based red flags --------
    red_flags = extract_red_flags(text)

    # -------- Final score (IMPORTANT PART) --------
    # Base from ML
    final_score = ml_prob * 100

    # Boost score based on red flags
    final_score += len(red_flags) * 20

    # Cap at 100
    final_score = min(final_score, 100)

    # -------- Final label (CORRECT) --------
    if final_score >= 70:
        final_label = "High Risk"
    elif final_score >= 35:
        final_label = "Suspicious"
    else:
        final_label = "Safe"

    # -------- Explanation --------
    if final_label == "Safe":
        base_explanation = (
            "This email appears safe. No strong scam indicators such as "
            "payment requests or urgent pressure were detected."
        )
    elif final_label == "Suspicious":
        base_explanation = (
            "This email shows warning signs such as "
            + ", ".join(red_flags)
            + ". It should be reviewed carefully before proceeding."
        )
    else:
        base_explanation = (
            "This email shows strong scam indicators including "
            + ", ".join(red_flags)
            + ". It poses a high risk and should be avoided."
        )

    ai_explanation = rewrite_explanation(base_explanation)
    final_explanation = ai_explanation if ai_explanation else base_explanation

    # -------- Store result --------
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

