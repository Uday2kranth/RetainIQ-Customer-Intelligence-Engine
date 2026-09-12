# 🌲 Stage 3: Machine Learning Model & Inference

> **Voice Mode Explainer:**
> This stage powers the predictive brain of RetainIQ: training a Random Forest classifier, prioritizing Recall to catch leaving customers, and calculating continuous churn risk percentages.

---

## 1. What Happens at This Stage?
1. **Training (`src/ml/train.py`):**
   * Prepares customer features (tenure, complaints, satisfaction, RFM scores, device count).
   * Handles categorical variables and scales numerical distributions.
   * Trains a **`RandomForestClassifier`** with balanced class weights.
   * Evaluates on held-out test data (evaluating ROC-AUC and Recall).
   * Persists the trained artifact to `models/churn_model.pkl`.
2. **Inference (`src/ml/inference.py`):**
   * Loads `models/churn_model.pkl`.
   * Calls `predict_proba()` to compute continuous churn probability (0.0 to 1.0) for every account.
   * Multiplies by 100 to get `churn_risk_pct` (e.g. `97.57%`).
   * Categorizes accounts into dynamic risk tiers:
     * **High Risk ($\ge 80\%$):** 339 accounts flagged for urgent outreach.
     * **Medium Risk ($50\% - 79\%$):** 586 accounts flagged for engagement emails.
     * **Low Risk ($< 50\%$):** 4,705 healthy accounts.
   * Writes predictions to SQLite table `churn_predictions`.

---

## 2. Key Engineering Decisions & Why We Made Them

### Why Random Forest Over Logistic Regression or Neural Networks?
* **Tabular Performance:** Tree ensembles consistently outperform deep learning on small-to-medium tabular datasets (~5,600 rows).
* **Non-Linear Interactions:** Churn is rarely a single linear factor. It is usually a combination: *e.g., Low Tenure + Active Complaint + High Days Since Order*. Trees naturally capture these non-linear splits.
* **Calibrated Continuous Output:** Random Forest averages probabilistic predictions across hundreds of decision trees, giving smooth, well-calibrated percentages via `predict_proba()`.

### Why Optimize for Recall Over Accuracy?
* In churn prediction, datasets are imbalanced (~14% churn).
* If a model predicts "Nobody Churns", it achieves **86% accuracy**, but catches **0 churners**!
* **Business Cost Asymmetry:**
  * **False Negative (Costly):** The model misses a churner $\rightarrow$ customer leaves $\rightarrow$ company loses hundreds of dollars in lifetime revenue.
  * **False Positive (Cheap):** The model flags a loyal customer $\rightarrow$ company sends a 10% discount coupon $\rightarrow$ minimal cost.
* Therefore, we tuned class weights and thresholds specifically to maximize **Recall** (catching leaving customers).

---

## 3. What to Say to Your Mentor (30 Seconds)

> *"In Stage 3, our machine learning engine uses a Scikit-Learn Random Forest Classifier trained on behavioral and RFM attributes.*
> 
> *Because churn prediction is an asymmetric business problem, we prioritized Recall over Accuracy to minimize costly False Negatives. Rather than returning rigid 0 or 1 labels, we use `predict_proba()` to generate continuous risk scores from 0% to 100%.*
> 
> *Our batch inference scores all 5,630 accounts in under one second, flagging 339 high-risk accounts exceeding our 80% intervention threshold for automated daily outreach."*
