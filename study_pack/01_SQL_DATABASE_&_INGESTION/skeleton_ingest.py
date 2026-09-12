"""
SKELETON CODE: Stage 1 - Ingestion, Synthetic Generator & Batch Simulation
File Reference: src/etl/ingest.py & src/db/schema.py
"""
import os
import pandas as pd
import numpy as np
from sqlalchemy import text
from src.db.connection import get_engine
from src.db.schema import init_db

engine = get_engine()
init_db(engine)

# --- 1. BASELINE INGESTION (5,630 Records) ---
CSV_PATH = "data/raw/ecommerce_customer_churn.csv"
if os.path.exists(CSV_PATH):
    df = pd.read_csv(CSV_PATH)
else:
    # Synthetic Generator: Generates realistic Kaggle distributions on demand
    n = 5630
    df = pd.DataFrame({
        "customer_id": np.arange(50001, 50001 + n),
        "tenure": np.random.exponential(scale=10.0, size=n).clip(0, 61).round(),
        "complain": np.random.choice([0, 1], size=n, p=[0.72, 0.28]),
        "satisfaction_score": np.random.choice([1, 2, 3, 4, 5], size=n),
        "order_count": np.random.poisson(lam=3, size=n).clip(1, 16),
        "cashback_amount": np.random.normal(loc=177, scale=49, size=n).round(2),
        "churn": np.random.choice([0, 1], size=n, p=[0.86, 0.14])
    })
df.to_sql("raw_customers", con=engine, if_exists="replace", index=False)
print(f"✅ Baseline Ingested: {len(df)} records in 'raw_customers' table.")

# --- 2. INCREMENTAL BATCH SIMULATOR (Live Demo Switch) ---
def simulate_incoming_batch(batch_size: int = 35):
    """Appends newly arriving customer transactions to SQL for dynamic Power BI refresh."""
    with engine.connect() as conn:
        max_id = conn.execute(text("SELECT MAX(customer_id) FROM raw_customers")).scalar() or 55630
    
    new_df = pd.DataFrame({
        "customer_id": np.arange(max_id + 1, max_id + 1 + batch_size),
        "tenure": np.random.choice([0, 1, 2, 3, 5], size=batch_size),
        "complain": np.random.choice([0, 1], size=batch_size, p=[0.65, 0.35]),
        "satisfaction_score": np.random.choice([1, 2, 3], size=batch_size),
        "order_count": np.random.poisson(lam=2, size=batch_size).clip(1, 8),
        "cashback_amount": np.random.normal(loc=160, scale=40, size=batch_size).round(2),
        "churn": np.random.choice([0, 1], size=batch_size, p=[0.70, 0.30])
    })
    new_df.to_sql("raw_customers", con=engine, if_exists="append", index=False)
    print(f"🚀 Batch Ingested: Appended {batch_size} incoming records. Total: {max_id + batch_size - 50000}.")
