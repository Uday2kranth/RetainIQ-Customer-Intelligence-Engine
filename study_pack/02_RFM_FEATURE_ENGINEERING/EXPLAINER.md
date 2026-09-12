# 📊 Stage 2: RFM Feature Engineering

> **Voice Mode Explainer:**
> This stage transforms static transactional numbers into behavioral customer intelligence using Recency, Frequency, and Monetary (RFM) quintile segmentation.

---

## 1. What Happens at This Stage?
1. **Reads from SQL:** Pulls raw customer records from `raw_customers`.
2. **Computes RFM Scores:** Calculates:
   * **R (Recency):** Days since the last order (`day_since_last_order`). Lower is better!
   * **F (Frequency):** Total number of orders placed (`order_count`). Higher is better!
   * **M (Monetary / Value):** Total cashback incentive received (`cashback_amount`). Higher is better!
3. **Applies Quintile Binning (`pd.qcut`):** Ranks each customer from 1 (lowest) to 5 (highest) relative to all other customers.
4. **Assigns Behavioral Segments:** Maps combined RFM scores into actionable marketing segments:
   * **Champions (Score 5-5):** Highest loyalty, high spending, recent activity.
   * **Loyal Customers:** Frequent buyers with strong history.
   * **At Risk:** Previously high frequency, but haven't bought in a long time!
   * **Hibernating:** Low recency, low frequency, low engagement.
   * **Promising / Need Attention:** Moderate activity requiring targeted discounts.
5. **Persists Features:** Writes the segmentations back into SQLite table `rfm_features` and saves `data/processed/rfm_features.parquet`.

---

## 2. Key Engineering Decisions & Why We Made Them

### Why Not Just Use Raw Order Numbers?
* **Raw Numbers Lack Context:** A customer who placed 10 orders two years ago is completely different from a customer who placed 10 orders this past month.
* **Quintile Normalization:** Using Pandas `pd.qcut()` eliminates outlier skew and normalizes behavioral metrics into uniform 1–5 scores.
* **Strong ML Signal:** RFM segments give our Random Forest model strong categorical signals regarding changes in customer velocity before churn occurs.

---

## 3. What to Say to Your Mentor (30 Seconds)

> *"In Stage 2, our feature engineering pipeline transforms raw transactional attributes into behavioral intelligence using RFM analysis.*
> 
> *Using Pandas quintile binning (`pd.qcut`), we score every customer from 1 to 5 across Recency, Frequency, and Monetary dimensions. This segments our customer base into behavioral tiers such as Champions, Loyalists, and At-Risk accounts.*
> 
> *By capturing the velocity of customer engagement rather than static order counts, we provide our machine learning model with critical early-warning indicators of churn."*
