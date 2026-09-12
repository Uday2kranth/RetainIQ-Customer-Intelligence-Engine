# 🌪️ Stage 5: Apache Airflow Pipeline Orchestration (RetainIQ Engine)

> **Voice Mode Explainer:**
> This document provides the complete, end-to-end conceptual and technical defense for Apache Airflow in the RetainIQ project. Use this for oral rehearsal with Gemini Voice on your phone.

---

## 1. The "Kitchen Manager" Analogy (The Mental Model)

> Imagine a high-end restaurant kitchen:
> - **Chef 1:** Chops and washes the raw vegetables (**Task 1: SQL Data Ingestion**).
> - **Chef 2:** Measures ingredients and simmers sauces (**Task 2: RFM Feature Engineering**).
> - **Master Chef:** Cooks the gourmet steak (**Task 3: Machine Learning Model Inference**).
> - **Head Waiter:** Delivers the hot meal to the VIP guest (**Task 4: Gmail OAuth Alerting & Power BI**).
>
> If Chef 1 hasn't chopped the vegetables, the Master Chef *cannot cook*. If someone tries to cook without chopped vegetables, the restaurant collapses into chaos.
> 
> **Apache Airflow is the Kitchen Manager.** 
> Airflow doesn't cook the food itself — it oversees the kitchen:
> 1. **Order of Operations (`>>`):** Ensures Task 2 only begins after Task 1 succeeds.
> 2. **Deterministic Schedule:** Sets the kitchen clock to start every morning at 6:00 AM UTC.
> 3. **Fault Recovery:** If a stove burner fails (database connection glitch), the manager waits 5 minutes and retries the burner automatically (`retries=2, retry_delay=5 minutes`).
> 4. **Audit Trail:** Logs the exact second every dish started, finished, or encountered an error.

---

## 2. Airflow Architecture in RetainIQ (`dags/retainiq_pipeline_dag.py`)

Our Airflow DAG is structured using the modern **Airflow 2.x TaskFlow API**:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Airflow DAG: @daily                             │
│                                                                        │
│  ┌────────────────────┐          ┌──────────────────────────────────┐  │
│  │ task_ingest_data   │   >>     │ task_feature_engineering         │  │
│  │ - Reads raw CSV    │          │ - Computes RFM Quintiles (1-5)   │  │
│  │ - Writes to SQL DB │          │ - Assigns Loyalty Segments       │  │
│  └─────────┬──────────┘          └────────────────┬─────────────────┘  │
│            │                                      │                    │
│            └───────────────────┬──────────────────┘                    │
│                                │                                       │
│                                ▼                                       │
│  ┌────────────────────┐          ┌──────────────────────────────────┐  │
│  │ task_send_alerts   │   <<     │ task_model_inference             │  │
│  │ - Filters risk ≥80%│          │ - Loads churn_model.pkl          │  │
│  │ - Sends Gmail OAuth│          │ - predict_proba() risk scores    │  │
│  │ - Logs alert audit │          │ - Writes predictions to SQL      │  │
│  └────────────────────┘          └──────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

### The 4 Pipeline Tasks Defined in Our DAG:
1. **`task_ingest_data()`**: Ingests 5,630 raw e-commerce records into the SQL database (`raw_customers` table) with idempotency checks.
2. **`task_feature_engineering()`**: Extracts records, computes Recency, Frequency, and Monetary quintiles (1 to 5), tags customers with loyalty personas (Champions, Loyalists, Hibernating, At-Risk), and saves results to `rfm_features`.
3. **`task_model_inference()`**: Deserializes `models/churn_model.pkl`, executes `predict_proba()` to compute continuous churn risk (0% to 100%), tags accounts into High/Medium/Low tiers, and populates `churn_predictions`.
4. **`task_send_alerts()`**: Queries accounts exceeding the 80% threshold, compiles the executive HTML briefing table, dispatches automated alerts via Gmail OAuth 2.0 to sales managers, and writes an audit record into `alert_history`.

---

## 3. Top 5 Airflow Defense Questions & Winning Answers

### Q1: Why use Apache Airflow instead of a simple Python script or Windows Task Scheduler / Cron?
> **Winning Answer:**  
> *"A cron job or Python script is 'fire-and-forget'—it offers zero observability, no automatic error recovery, and no task isolation. If a linear script fails at step 2, step 3 might run on corrupt data, or the entire script silently dies without anyone noticing.*  
> *Airflow transforms our pipeline into a Directed Acyclic Graph (DAG) with:*  
> *1. **Strict Dependency Guarantees:** Downstream inference will NEVER execute if data ingestion fails.*  
> *2. **Built-in Retry Policies:** Our tasks have `retries=2, retry_delay=5 minutes`, giving transient database or network blips time to resolve.*  
> *3. **Observability & Backfilling:** Airflow provides a web UI showing color-coded task states (green for success, red for failure) and allows deterministic backfilling of historical data."*

---

### Q2: How do your tasks pass data to each other? Do you pass large DataFrames through Airflow XComs?
> **Winning Answer (Crucial Data Engineering Distinction):**  
> *"**Absolutely not.** Passing large DataFrames through XComs is a major anti-pattern because XComs serialize data into Airflow’s backend metadata database (like PostgreSQL or MySQL), which causes severe database bloat and memory bottlenecks.*  
> *In RetainIQ, we followed the industry-standard **Data Lake / Database Pushdown Pattern**:*  
> *- **Heavy data** (5,630 customer rows and RFM matrices) is written directly to the SQL database or Parquet storage.*  
> *- **XComs only pass lightweight operational metadata**—specifically JSON dictionaries containing record counts, churn percentages, execution status, and Gmail message IDs for auditing."*

---

### Q3: What happens if Task 3 (Model Inference) crashes mid-execution?
> **Winning Answer:**  
> *"First, Airflow halts the DAG execution immediately at Task 3. Because of the `>>` dependency operator, Task 4 (`task_send_alerts`) will NOT trigger, preventing misleading or un-scored alerts from being emailed to sales leadership.*  
> *Second, Airflow triggers our automated retry policy: it waits 5 minutes and retries Task 3 up to 2 times.*  
> *Third, if all retries are exhausted, Task 3 is marked as FAILED in the Airflow metadata store, and an on-failure alert callback notifies the engineering team with the exact stack trace."*

---

### Q4: How is Airflow implemented in this repository, especially on Windows?
> **Winning Answer:**  
> *"Airflow is natively designed for Linux/POSIX environments (running on Docker, Kubernetes, or Celery workers). In production, our `dags/retainiq_pipeline_dag.py` runs inside an official Apache Airflow container.*  
> *To allow seamless local development and Windows demonstration without requiring heavy Docker virtualization, we engineered a dual-mode pattern:*  
> *1. **Enterprise Packaging (`requirements.txt`):** We specify `apache-airflow>=2.7.0; sys_platform != 'win32'`. This standard PEP 508 environment marker ensures Linux/Docker production containers install full Airflow, while Windows local developers don't suffer POSIX C-extension compile crashes (`pwd`, `fcntl`).*  
> *2. **Compatibility DAG Decorators:** In `dags/retainiq_pipeline_dag.py`, we provide fallback shims for `@dag` and `@task`.*  
> *3. **Master Pipeline Runner:** We built `run_pipeline.py`, which executes the identical 4-stage sequential task logic with full logging, providing 100% testable parity with an Airflow executor in just 2.3 seconds!"*

---

### Q5: What is the TaskFlow API and why did you use it over traditional PythonOperator?
> **Winning Answer:**  
> *"Traditional Airflow 1.x required instantiating boilerplate `PythonOperator` classes and manually calling `xcom_push` and `xcom_pull` with string keys. Airflow 2.x introduced the TaskFlow API (`@dag` and `@task` decorators).*  
> *TaskFlow allows us to write standard, clean Python functions and decorate them with `@task`. Airflow automatically handles task ID assignment, serialization, and XCom parameter mapping behind the scenes. It results in cleaner, modular, unit-testable code that looks like standard Python."*

---

## 4. Verbatim 45-Second Mentor Pitch (Memorize This!)

> *"To elevate RetainIQ from a standalone machine learning script to an enterprise-grade automated engine, we orchestrated our daily pipeline using Apache Airflow's modern TaskFlow API in `dags/retainiq_pipeline_dag.py`.*
> 
> *Our DAG runs on a daily schedule, enforcing strict one-way execution across four isolated tasks: SQL ingestion, RFM feature engineering, Random Forest inference, and automated Gmail alert dispatch.*
> 
> *By decoupling heavy data storage in SQL from lightweight operational metadata in XComs, and applying automated retry policies, Airflow ensures our machine learning models and executive alerts are deterministic, fault-tolerant, and completely hands-free."*
