"""
SKELETON CODE: Stage 3 - Model Training & Batch Inference
File Reference: src/ml/train.py & src/ml/inference.py
"""
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import recall_score, roc_auc_score
from src.db.connection import get_engine

engine = get_engine()

# --- PART A: TRAINING ---
# 1. Load merged features from SQL
df = pd.read_sql("SELECT r.*, f.r_score, f.f_score, f.m_score FROM raw_customers r JOIN rfm_features f ON r.customer_id = f.customer_id", con=engine)
features = ["tenure", "complain", "satisfaction_score", "order_count", "cashback_amount", "r_score", "f_score", "m_score"]

X = df[features]
y = df["churn"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# 2. Train Random Forest tuned for Recall
clf = RandomForestClassifier(n_estimators=100, class_weight="balanced", random_state=42)
clf.fit(X_train, y_train)

# 3. Evaluate & save model
test_preds = clf.predict(X_test)
print(f"✅ Trained Model | Test Recall: {recall_score(y_test, test_preds):.2%}")
joblib.dump(clf, "models/churn_model.pkl")

# --- PART B: INFERENCE ---
# 4. Predict continuous churn probabilities for all accounts
probs = clf.predict_proba(X)[:, 1] # Probability of churn (class 1)

df["churn_probability"] = probs
df["churn_risk_pct"] = (probs * 100).round(2)
df["risk_tier"] = df["churn_probability"].apply(lambda p: "High" if p >= 0.80 else ("Medium" if p >= 0.50 else "Low"))

# 5. Save predictions to SQL database
df[["customer_id", "churn_probability", "churn_risk_pct", "risk_tier"]].to_sql("churn_predictions", con=engine, if_exists="replace", index=False)
print(f"✅ Inferred risk scores: {sum(df['risk_tier'] == 'High')} High-Risk customers identified.")
