import os
import pandas as pd
import re
import pickle

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, accuracy_score


# -----------------------------
# Text cleaning
# -----------------------------
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"http\S+", " ", text)
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# -----------------------------
# Label normalization
# -----------------------------
def normalize_label(val):
    """
    Converts various label formats to:
    1 = scam / fraudulent
    0 = safe / legitimate
    Returns None if unknown
    """
    if pd.isna(val):
        return None

    val = str(val).strip().lower()

    if val in ["1", "true", "t", "yes", "y", "fraud", "fraudulent", "scam", "fake"]:
        return 1

    if val in ["0", "false", "f", "no", "n", "legit", "legitimate", "real", "safe"]:
        return 0

    return None


# -----------------------------
# Load and normalize dataset (ROBUST)
# -----------------------------
def load_dataset(path):
    df = pd.read_csv(path)
    filename = os.path.basename(path)

    print(f"\nLoading {filename}")
    print("Columns:", list(df.columns))

    # ---------- LABEL DETECTION ----------
    label_col = None
    for col in df.columns:
        if col.lower() in [
            "label", "fraudulent", "scam", "target",
            "is_fake", "is_scam", "class"
        ]:
            label_col = col
            break

    if label_col is None:
        print("Skipped: no label column")
        return None

    # ---------- TEXT DETECTION ----------
    text_cols = []
    for col in df.columns:
        if col.lower() in [
            "text", "description", "job_description",
            "content", "email", "title",
            "company_profile", "requirements", "benefits"
        ]:
            text_cols.append(col)

    if not text_cols:
        print("Skipped: no usable text columns")
        return None

    # Combine text columns
    df["text"] = df[text_cols].astype(str).agg(" ".join, axis=1)

    # Normalize labels
    df["label"] = df[label_col].apply(normalize_label)

    # Drop rows with unknown labels
    before = len(df)
    df = df.dropna(subset=["label"])
    after = len(df)

    if after < before:
        print(f"Dropped {before - after} rows with unknown labels")

    return df[["text", "label"]]


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":

    dataset_folder = "dataset"
    all_dfs = []

    print("\nScanning dataset folder...")

    for file in os.listdir(dataset_folder):
        if file.lower().endswith(".csv"):
            df = load_dataset(os.path.join(dataset_folder, file))
            if df is not None and not df.empty:
                all_dfs.append(df)

    if not all_dfs:
        raise RuntimeError("No valid datasets loaded.")

    # Merge datasets
    data = pd.concat(all_dfs, ignore_index=True)

    # Clean text
    data["text"] = data["text"].apply(clean_text)
    data["label"] = data["label"].astype(int)

    print("\nTotal samples:", len(data))
    print("Label distribution:")
    print(data["label"].value_counts())

    # -----------------------------
    # Train-test split
    # -----------------------------
    X_train, X_test, y_train, y_test = train_test_split(
        data["text"],
        data["label"],
        test_size=0.2,
        random_state=42,
        stratify=data["label"]
    )

    # -----------------------------
    # Vectorization
    # -----------------------------
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        stop_words="english"
    )

    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    # -----------------------------
    # Model training
    # -----------------------------
    model = MultinomialNB()
    model.fit(X_train_vec, y_train)

    # -----------------------------
    # Evaluation
    # -----------------------------
    y_pred = model.predict(X_test_vec)

    print("\nAccuracy:", accuracy_score(y_test, y_pred))
    print("\nClassification Report:\n")
    print(classification_report(y_test, y_pred))

    # -----------------------------
    # Save model + vectorizer
    # -----------------------------
    os.makedirs("model", exist_ok=True)

    with open("model/scam_model.pkl", "wb") as f:
        pickle.dump(model, f)

    with open("model/vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)

    print("\nModel and vectorizer saved successfully.")