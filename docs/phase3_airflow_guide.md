# 🌪️ Phase 3 User Guide: Apache Airflow Orchestration & Pipeline Architecture

This document explains the orchestration engine powering **RetainIQ**. It breaks down the architecture of [`dags/retainiq_pipeline_dag.py`](file:///d:/important_cmd_history/project%20fopr%20suretrust/dags/retainiq_pipeline_dag.py), how the 4 sequential tasks interact, how to run the pipeline, and how to explain it to evaluators.

---

## 🧭 Overview: What is Airflow Doing in RetainIQ?

Apache Airflow is a workflow orchestration platform. In RetainIQ, it ensures that your machine learning model and alerts don't run haphazardly; instead, they execute as a **strictly ordered, deterministic Directed Acyclic Graph (DAG)** every day.

```
┌─────────────────────────┐
│ Task 1 (SQL Ingestion)  │ ➔ Pulls fresh 5,600+ records into SQL database
└────────────┬────────────┘
             │ (Passes row count metadata via XCom)
             ▼
┌─────────────────────────┐
│   Task 2 (RFM Engine)   │ ➔ Computes Pandas RFM quintiles & segments
└────────────┬────────────┘
             │ (Passes segment distribution via XCom)
             ▼
┌─────────────────────────┐
│ Task 3 (Model Inference)│ ➔ Predicts churn probabilities (%) via Scikit-Learn
└────────────┬────────────┘
             │ (Passes high-risk account IDs via XCom)
             ▼
┌─────────────────────────┐
│  Task 4 (Email Action)  │ ➔ Triggers Gmail OAuth 2.0 alert to Sales Manager
└─────────────────────────┘
```

---

## ⚙️ The 4 Airflow Tasks in Detail

### 1. `task_1_sql_ingestion`
* **Python Function**: `src.etl.ingest.ingest_raw_data()`
* **What it does**: Ingests customer account records (5,630 records across 20+ columns) into the `raw_customers` table using SQLAlchemy.
* **Why it matters**: Ensures the database is always refreshed with the latest customer transactional snapshots before modeling begins.

### 2. `task_2_rfm_feature_engineering`
* **Python Function**: `src.etl.feature_engineering.engineer_features()`
* **What it does**: Reads raw customer data, calculates **Recency** (`day_since_last_order`), **Frequency** (`order_count`), and **Monetary** (`cashback_amount`), generates 1-5 quintile scores, classifies RFM segments (e.g. *Champions*, *Loyal*, *At Risk*), and writes the `rfm_features` table to SQL.
* **Why it matters**: Raw transactional numbers alone don't explain customer loyalty; RFM behavioral indicators provide essential predictive signal to the ML classifier.

### 3. `task_3_model_inference`
* **Python Function**: `src.ml.inference.predict_churn_risk()`
* **What it does**: Loads the serialized `churn_model.pkl` artifact, calculates probability scores (`predict_proba()`), assigns risk tiers (`High` for $\ge 80\%$, `Medium` for $50-79\%$, `Low` for $< 50\%$), and updates the `churn_predictions` SQL table.
* **Why it matters**: Converts complex feature interactions into an actionable 0-100% risk metric stored permanently in SQL.

### 4. `task_4_gmail_alert_action`
* **Python Function**: `src.alerts.gmail_alert.send_churn_alerts()`
* **What it does**: Executes a SQL query for all customers exceeding the 80% risk threshold, compiles a formatted HTML table of top accounts with suggested interventions, and dispatches the alert email via the official Google Gmail API.
* **Why it matters**: Closes the loop from passive analytics to active business operations by proactively notifying the sales team before the customer leaves.

---

## 🚀 How to Execute the Pipeline

### Method 1: Instant Local Pipeline Runner (Recommended for fast local testing & demos)
You can run the entire 4-stage pipeline directly in Python with zero Airflow daemon overhead:
```bash
python run_pipeline.py
```
* **Execution Time**: ~2 to 3 seconds.
* **Output**: Detailed terminal logs showing record counts, RFM distributions, ML risk breakdown, and alert dispatches.

### Method 2: Running via Full Apache Airflow Standalone
If demonstrating within the full Apache Airflow Web UI:
1. In your terminal (or WSL2), start Airflow:
   ```bash
   airflow standalone
   ```
2. Open your browser and navigate to:
   `http://localhost:8080`
3. Locate `retainiq_daily_customer_intelligence_pipeline` in the DAG list.
4. Toggle the DAG switch to **Active (ON)** and click the **Play (Trigger DAG)** button.
5. Click on **Grid** or **Graph** view to watch each task box turn from light blue (queued) ➔ dark green (success).

---

## 🗣️ How to Explain Phase 3 in Interviews or Project Reviews

> *"In Phase 3, we built an enterprise workflow DAG using Airflow's modern TaskFlow API (`@dag` and `@task`). Each step is modular, idempotent, and decoupled into discrete units of work. If raw ingestion fails, downstream inference will not run on stale data. The pipeline passes execution metadata through XComs and logs every alert in a dedicated SQL audit table for complete governance."*
