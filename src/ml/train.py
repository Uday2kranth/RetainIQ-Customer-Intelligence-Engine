import os
import json
import logging
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report, roc_auc_score, recall_score, precision_score, f1_score, accuracy_score
)
from src.config import PROCESSED_DATA_PATH, PROCESSED_CSV_PATH, MODEL_PATH, MODEL_METRICS_PATH
from src.etl.feature_engineering import engineer_features

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def train_churn_model() -> dict:
    """
    Offline Model Training:
    Trains Random Forest Classifier optimized for high recall on churned customers,
    evaluates classification performance, and exports churn_model.pkl and metrics.
    """
    if not os.path.exists(PROCESSED_DATA_PATH) and not os.path.exists(PROCESSED_CSV_PATH):
        logger.info("Processed dataset not found. Running feature engineering first...")
        engineer_features()

    if os.path.exists(PROCESSED_DATA_PATH):
        df = pd.read_parquet(PROCESSED_DATA_PATH)
    else:
        df = pd.read_csv(PROCESSED_CSV_PATH)
    
    # Drop non-feature identifiers and target
    ignore_cols = ["customer_id", "churn", "ingested_at", "calculated_at"]
    feature_cols = [c for c in df.columns if c not in ignore_cols]
    
    X = df[feature_cols]
    y = df["churn"]

    logger.info(f"Training dataset shape: X={X.shape}, y={y.shape} (Churn rate: {y.mean():.2%})")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    # Random Forest tuned for high recall & robust probability calibration
    clf = RandomForestClassifier(
        n_estimators=150,
        max_depth=12,
        min_samples_split=4,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )

    logger.info("Fitting Random Forest Classifier...")
    clf.fit(X_train, y_train)

    # Evaluate
    y_pred = clf.predict(X_test)
    y_prob = clf.predict_proba(X_test)[:, 1]

    metrics = {
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, y_prob)), 4),
        "recall_churn": round(float(recall_score(y_test, y_pred)), 4),
        "precision_churn": round(float(precision_score(y_test, y_pred)), 4),
        "f1_score": round(float(f1_score(y_test, y_pred)), 4),
        "features_count": len(feature_cols),
        "train_samples": len(X_train),
        "test_samples": len(X_test)
    }

    logger.info("=== MODEL PERFORMANCE REPORT ===")
    logger.info(f"ROC-AUC Score : {metrics['roc_auc']}")
    logger.info(f"Recall (Churn): {metrics['recall_churn']}")
    logger.info(f"Precision     : {metrics['precision_churn']}")
    logger.info(f"Accuracy      : {metrics['accuracy']}")

    # Save model artifact bundled with feature schema
    model_payload = {
        "model": clf,
        "feature_cols": feature_cols,
        "metrics": metrics
    }
    joblib.dump(model_payload, MODEL_PATH)
    logger.info(f"Saved finalized model artifact to {MODEL_PATH}")

    with open(MODEL_METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=2)
    logger.info(f"Saved evaluation metrics to {MODEL_METRICS_PATH}")

    return metrics

if __name__ == "__main__":
    train_churn_model()
