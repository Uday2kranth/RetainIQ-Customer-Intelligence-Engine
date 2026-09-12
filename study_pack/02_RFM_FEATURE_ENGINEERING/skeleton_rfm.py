"""
SKELETON CODE: Stage 2 - RFM Feature Engineering
File Reference: src/etl/feature_engineering.py
"""
import pandas as pd
from src.db.connection import get_engine

engine = get_engine()

# 1. Load raw customers from SQL
df = pd.read_sql("SELECT customer_id, day_since_last_order, order_count, cashback_amount FROM raw_customers", con=engine)

# 2. Compute RFM Quintiles (1 to 5) using pd.qcut
# For Recency: lower days since last order = higher score (5 is best)
df["r_score"] = pd.qcut(df["day_since_last_order"].rank(method="first"), q=5, labels=[5, 4, 3, 2, 1]).astype(int)

# For Frequency & Monetary: higher count/amount = higher score (5 is best)
df["f_score"] = pd.qcut(df["order_count"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
df["m_score"] = pd.qcut(df["cashback_amount"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]).astype(int)

# 3. Map RFM scores into business segments
def assign_segment(row):
    r, f = row["r_score"], row["f_score"]
    if r >= 4 and f >= 4:
        return "Champions"
    elif r >= 3 and f >= 3:
        return "Loyal Customers"
    elif r <= 2 and f >= 3:
        return "At Risk"
    elif r <= 2 and f <= 2:
        return "Hibernating"
    else:
        return "Promising"

df["rfm_segment"] = df.apply(assign_segment, axis=1)

# 4. Save back to SQL database
df.to_sql("rfm_features", con=engine, if_exists="replace", index=False)

print(f"✅ Populated 'rfm_features' table for {len(df)} customers.")
