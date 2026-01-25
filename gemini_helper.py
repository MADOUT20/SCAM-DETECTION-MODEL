import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemini-1.5-flash")

def rewrite_explanation(base_explanation):
    prompt = f"""
Rewrite the following explanation in a clear, professional,
slightly more detailed advisory tone.
Do NOT add new reasons or change the meaning.

Explanation:
\"\"\"{base_explanation}\"\"\"
"""
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        return text if text else None
    except Exception:
        return None