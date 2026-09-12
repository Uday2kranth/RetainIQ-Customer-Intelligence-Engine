# 📘 RetainIQ: Customer Intelligence Engine - Master Architecture & Defense Guide

**RetainIQ** is an enterprise-grade Customer Churn Prediction and Automated Retention Engine built for modern e-commerce stores. It shifts customer retention strategy from **reactive damage control** (acting after the customer leaves) to **proactive predictive intervention** (identifying risk early and triggering automated workflows).

---

## 🏗️ 1. Complete System Architecture

```
[ Kaggle E-Commerce Dataset (~5,630 Customer Accounts) ]
                           │
                           ▼
┌───────────────────────────────────────────────────────────┐
│              APACHE AIRFLOW PIPELINE (DAILY DAG)          │
│                                                           │
│  Task 1: SQL Ingestion                                    │
│  └─▶ Pulls fresh customer snapshots into raw_customers    │
│                                                           │
│  Task 2: RFM Feature Engineering                          │
│  └─▶ Calculates Recency, Frequency, Monetary (Pandas)     │
│                                                           │
│  Task 3: Machine Learning Inference                       │
│  └─▶ Predicts Churn Probabilities via Random Forest       │
│                                                           │
│  Task 4: High-Risk Alert Action                           │
│  └─▶ Sends HTML Alert via Gmail OAuth for Risk >= 80%     │
└──────────────────────────┬────────────────────────────────┘
                           │
                           ▼
┌───────────────────────────────────────────────────────────┐
│               SQL DATABASE ENGINE (SCHEMA & VIEWS)        │
│                                                           │
│  - raw_customers      : Demographic & order history       │
│  - rfm_features       : Behavioral segments & scores      │
│  - churn_predictions  : Probabilities & risk tiers        │
│  - alert_history      : Audit trail of dispatched alerts  │
│  - v_daily_action_queue: Pre-aggregated operational view  │
└──────────────────────────┬────────────────────────────────┘
                           │
                           ▼
┌───────────────────────────────────────────────────────────┐
│           POWER BI CONTROL TOWER (DESKTOP DASHBOARD)      │
│                                                           │
│  - Executive KPI Cards (Total Accounts, Churn %, NPS)     │
│  - Churn Diagnostics (By Tenure, Category, Complaints)    │
│  - Daily High-Priority Support & Sales Action Queue       │
└───────────────────────────────────────────────────────────┘
```

---

## 🛠️ 2. Key Technical Decisions & Why They Were Made

| Component | Technology Chosen | Why This Decision Was Made? |
| :--- | :--- | :--- |
| **Data Ingestion & Storage** | **SQLAlchemy + PostgreSQL / SQLite** | Enables reliable ACID compliance, clean schema migrations, and high-performance querying for Power BI. |
| **Feature Engineering** | **Pandas RFM Quintiles** | Traditional transactional columns lack behavioral context; RFM quintiles (1-5) provide clear customer loyalty segmentation. |
| **Machine Learning Model** | **Scikit-Learn `RandomForestClassifier`** | Non-linear tree ensemble handles tabular class imbalance effectively, outputs calibrated probabilities, and is interpretable. |
| **Evaluation Focus** | **Recall Optimization** | In customer churn, a **False Negative** (failing to detect a leaving customer) is far more costly than a **False Positive** (giving an extra discount). |
| **Pipeline Automation** | **Apache Airflow (TaskFlow API)** | Provides deterministic DAG scheduling, retry policies, task isolation, and XCom parameter passing. |
| **Alerting Channel** | **Gmail API with OAuth 2.0** | Enterprise-grade token-based authentication with zero plaintext passwords stored in code. |
| **Executive Reporting** | **Power BI Desktop + DAX** | Provides interactive filtering and cross-filtering for executive leadership and front-line sales teams. |

---

## 💡 3. Interview & Project Defense Q&A

### Q1: What problem does RetainIQ solve for e-commerce companies?
> **Answer**: *"E-commerce businesses typically operate reactively—reaching out with discount codes only after a customer has deleted their account or stopped buying for 6 months. RetainIQ predicts churn risk in real-time based on early behavioral friction (e.g. complaints, drop in order frequency, tenure drop-off) and automates daily intervention workflows before revenue is lost."*

---

### Q2: Why did you compute RFM metrics in Task 2?
> **Answer**: *"Raw customer attributes like order count or cashback don't tell the full story in isolation. RFM analysis categorizes customers into relative behavioral tiers (Champions, Loyal, At-Risk, Hibernating) using quintile distributions (1 to 5). This gives the Random Forest model strong predictive signal on loyalty velocity."*

---

### Q3: Why optimize for Recall rather than Accuracy in the ML model?
> **Answer**: *"In churn prediction, datasets are typically imbalanced (~13-20% churn rate). A naive model predicting 'no churn' for everyone would achieve ~85% accuracy but catch zero churners. By tuning class weights and thresholding, we prioritize **Recall**, ensuring we catch the highest possible percentage of leaving customers."*

---

### Q4: How does the Apache Airflow DAG handle failures?
> **Answer**: *"In our `retainiq_pipeline_dag.py`, tasks are strictly isolated. If Task 1 fails, Task 2 will not execute on stale data. The DAG is configured with automatic retries (`retries=2`, `retry_delay=5 minutes`) and logs every alert dispatch into an `alert_history` audit table in the SQL database for traceability."*

---

### Q5: How does Power BI connect to the system?
> **Answer**: *"Power BI connects directly to our SQL analytical views (such as `v_daily_action_queue` and `v_executive_kpis`). Instead of complex transformations in Power BI, data is pre-processed upstream by Python, allowing Power BI DAX measures to calculate metrics with sub-second performance."*
