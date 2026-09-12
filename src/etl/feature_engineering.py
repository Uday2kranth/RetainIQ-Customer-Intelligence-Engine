import os
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timezone
from src.config import PROCESSED_DATA_PATH, PROCESSED_CSV_PATH
from src.db.connection import get_engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def assign_rfm_segment(r: int, f: int, m: int) -> str:
    """Classifies customers into standard RFM behavioral segments."""
    rfm_score = f"{r}{f}{m}"
    if r >= 4 and f >= 4 and m >= 4:
        return "Champions"
    elif r >= 3 and f >= 3:
        return "Loyal Customers"
    elif r >= 3 and f >= 1:
        return "Potential Loyalist"
    elif r <= 2 and f >= 3:
        return "At Risk"
    elif r <= 2 and f <= 2 and m <= 2:
        return "Hibernating"
    elif r <= 2 and f >= 2:
        return "Need Attention"
    else:
        return "Promising"

def engineer_features(engine=None) -> dict:
    """
    Task 2 (Feature Engineering):
    Reads raw customer records from SQL database, computes RFM scores & segments,
    imputes missing data, encodes features, writes rfm_features table to SQL,
    and caches the processed dataset for model inference.
    """
    eng = engine or get_engine()
    logger.info("Extracting raw customer records from SQL database...")
    df = pd.read_sql("SELECT * FROM raw_customers", con=eng)
    
    if df.empty:
        raise ValueError("raw_customers table is empty. Please run Task 1 (Ingestion) first.")

    # 1. RFM Feature Calculations
    recency = df["day_since_last_order"].fillna(df["day_since_last_order"].median())
    frequency = df["order_count"].fillna(1)
    monetary = df["cashback_amount"].fillna(df["cashback_amount"].median())

    # R-Score (Inverted: fewer days since last order = higher score 1-5)
    r_score = pd.qcut(recency.rank(method="first"), q=5, labels=[5, 4, 3, 2, 1]).astype(int)
    # F-Score (More orders = higher score 1-5)
    f_score = pd.qcut(frequency.rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
    # M-Score (Higher cashback/spend = higher score 1-5)
    m_score = pd.qcut(monetary.rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]).astype(int)

    rfm_df = pd.DataFrame({
        "customer_id": df["customer_id"],
        "recency_days": recency,
        "frequency_orders": frequency,
        "monetary_cashback": monetary,
        "r_score": r_score,
        "f_score": f_score,
        "m_score": m_score
    })
    rfm_df["rfm_segment"] = [assign_rfm_segment(r, f, m) for r, f, m in zip(r_score, f_score, m_score)]
    rfm_df["calculated_at"] = datetime.now(timezone.utc)

    # Save RFM table to SQL
    rfm_df.to_sql("rfm_features", con=eng, if_exists="replace", index=False)
    logger.info(f"Populated rfm_features table for {len(rfm_df)} customers in SQL.")

    # 2. Comprehensive Preprocessed Feature Set for Machine Learning
    ml_df = df.copy()
    ml_df["recency_days"] = recency
    ml_df["frequency_orders"] = frequency
    ml_df["monetary_cashback"] = monetary
    ml_df["r_score"] = r_score
    ml_df["f_score"] = f_score
    ml_df["m_score"] = m_score
    ml_df["rfm_segment"] = rfm_df["rfm_segment"]

    # Impute missing values in numeric columns
    num_cols = ml_df.select_dtypes(include=[np.number]).columns
    for col in num_cols:
        if ml_df[col].isnull().any():
            ml_df[col] = ml_df[col].fillna(ml_df[col].median())

    # Encode categorical columns
    cat_cols = ["preferred_login_device", "preferred_payment_mode", "gender", "prefered_order_cat", "marital_status", "rfm_segment"]
    ml_encoded = pd.get_dummies(ml_df, columns=cat_cols, drop_first=True)

    # Cache preprocessed features (Parquet with CSV fallback)
    try:
        ml_encoded.to_parquet(PROCESSED_DATA_PATH, index=False)
        logger.info(f"Cached processed ML dataset to {PROCESSED_DATA_PATH}")
    except Exception as e:
        logger.warning(f"Could not save parquet ({e}). Saving to CSV fallback.")
    
    ml_encoded.to_csv(PROCESSED_CSV_PATH, index=False)

    return {
        "status": "SUCCESS",
        "total_records_processed": len(rfm_df),
        "rfm_segments_count": rfm_df["rfm_segment"].value_counts().to_dict(),
        "calculated_at": datetime.now(timezone.utc).isoformat()
    }

if __name__ == "__main__":
    engineer_features()
