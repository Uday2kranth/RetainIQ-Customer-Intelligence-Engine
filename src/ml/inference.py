import os
import logging
import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timezone
from src.config import MODEL_PATH, PROCESSED_DATA_PATH, PROCESSED_CSV_PATH, HIGH_RISK_THRESHOLD, MEDIUM_RISK_THRESHOLD
from src.db.connection import get_engine
from src.ml.train import train_churn_model

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def predict_churn_risk(engine=None) -> dict:
    """
    Task 3 (Model Inference):
    Loads churn_model.pkl, computes churn risk probabilities for customer records,
    classifies risk tiers, and updates the churn_predictions table in the SQL database.
    """
    eng = engine or get_engine()

    if not os.path.exists(MODEL_PATH):
        logger.info(f"Model artifact not found at {MODEL_PATH}. Initiating training...")
        train_churn_model()

    logger.info(f"Loading model artifact from {MODEL_PATH}...")
    model_payload = joblib.load(MODEL_PATH)
    model = model_payload["model"]
    feature_cols = model_payload["feature_cols"]

    if os.path.exists(PROCESSED_DATA_PATH):
        df = pd.read_parquet(PROCESSED_DATA_PATH)
    elif os.path.exists(PROCESSED_CSV_PATH):
        df = pd.read_csv(PROCESSED_CSV_PATH)
    else:
        raise FileNotFoundError("Processed dataset not found. Please run Task 2 (Feature Engineering) first.")

    customer_ids = df["customer_id"]

    # Align features with model schema
    for col in feature_cols:
        if col not in df.columns:
            df[col] = 0
    X = df[feature_cols]

    # Predict probabilities
    probabilities = model.predict_proba(X)[:, 1]
    risk_pcts = np.round(probabilities * 100, 2)

    # Classify Risk Tiers
    def classify_tier(prob):
        if prob >= HIGH_RISK_THRESHOLD:
            return "High"
        elif prob >= MEDIUM_RISK_THRESHOLD:
            return "Medium"
        else:
            return "Low"

    risk_tiers = [classify_tier(p) for p in probabilities]
    predicted_churn = (probabilities >= MEDIUM_RISK_THRESHOLD).astype(int)

    pred_df = pd.DataFrame({
        "customer_id": customer_ids,
        "churn_probability": np.round(probabilities, 4),
        "churn_risk_pct": risk_pcts,
        "risk_tier": risk_tiers,
        "predicted_churn": predicted_churn,
        "predicted_at": datetime.now(timezone.utc)
    })

    # Write predictions to SQL
    pred_df.to_sql("churn_predictions", con=eng, if_exists="replace", index=False)
    
    total_scored = len(pred_df)
    high_risk_count = int((pred_df["risk_tier"] == "High").sum())
    med_risk_count = int((pred_df["risk_tier"] == "Medium").sum())
    low_risk_count = int((pred_df["risk_tier"] == "Low").sum())
    avg_risk = round(float(pred_df["churn_risk_pct"].mean()), 2)

    logger.info(f"Model inference completed for {total_scored} customers.")
    logger.info(f"Risk Breakdown: High (>80%)={high_risk_count} | Medium={med_risk_count} | Low={low_risk_count} | Avg Risk={avg_risk}%")

    return {
        "status": "SUCCESS",
        "total_scored": total_scored,
        "high_risk_count": high_risk_count,
        "medium_risk_count": med_risk_count,
        "low_risk_count": low_risk_count,
        "avg_risk_pct": avg_risk,
        "predicted_at": datetime.now(timezone.utc).isoformat()
    }

if __name__ == "__main__":
    predict_churn_risk()
