# 💻 Stage 8: Streamlit Operations Console & Live Control Hub

> **The executive bridge connecting non-technical business stakeholders, automated Airflow scheduling, live machine learning predictions, and the Power BI Control Tower.**

---

## 🎯 Why Was the Streamlit Hub Built?

In an enterprise production environment, machine learning pipelines run **headless** in the cloud via Apache Airflow. However:
1. **Business Stakeholders Do Not Use Terminals**: Customer Success managers, Sales Directors, and non-technical evaluators cannot run command-line Python scripts.
2. **Real-Time Simulation & Demo**: The hub allows 1-click injection of incoming daily batches (+35 accounts) to demonstrate end-to-end model inference in 3.1 seconds.
3. **Operational Outreach**: Retention teams need a live, interactive queue to review high-risk accounts and dispatch targeted retention credits via Gmail OAuth with one click.

---

## 🏛️ Strategic Business Context & System Comparison

| Dimension | Legacy E-Commerce System (Traditional) | RetainIQ Modern System (Current) |
| :--- | :--- | :--- |
| **Ingestion** | Manual monthly CSV exports, prone to delays. | Autonomous daily batch ingestion into structured SQL database. |
| **Customer Scoring** | Static spreadsheets with zero behavioral weighting. | Behavioral RFM Quintile segmentation (11 loyalty personas). |
| **Churn Prediction** | Reactive: Teams discover churn after revenue is lost. | Proactive: Tuned Random Forest (81.8% Accuracy) flags accounts at $\ge 80\%$ risk. |
| **Action & Alerting** | Ad-hoc emails sent manually days or weeks later. | Automated priority HTML report dispatched via Gmail OAuth within 24 hours. |
| **Orchestration** | Manual human execution or brittle cron jobs. | Apache Airflow 2.x TaskFlow DAG with automatic retries and task isolation. |

---

## 🖥️ The 4 Core Hub Tabs & Architecture

### Tab 1: Executive Overview
* **KPI Cards**: Real-time accounts count (`5,630`), retention rate (`86.31%`), churn rate (`13.69%`), and high-risk accounts (`339`).
* **Power BI-Matched Diagnostic Charts**:
  - *Avg Churn Rate % by Product Category*: Grocery leads attrition at 16.0%, while Mobile Phone is lowest at 11.4%.
  - *Avg Churn Risk % by Customer Tenure*: Peaks heavily in months 0 to 6 ($\sim 40\%+$ risk) before stabilizing.

### Tab 2: High-Priority Customer Outreach Queue
* **Widescreen Display**: 680px tall view displaying 18+ high-risk customer profiles simultaneously without cramped inner scrolling.
* **Granular Filters**: Search by Customer ID or Segment persona, with risk threshold slider ($\ge 80\%$).
* **1-Click Direct Email Dispatch**: Primary button (*"Dispatch Action Queue to Alert Recipients Now"*) instantly sends the high-risk customer queue to all configured stakeholders via Google Gmail OAuth 2.0 API.

### Tab 3: Airflow Orchestration & Live Background Scheduler
* **Real Background Daemon (`scripts/schedule_demo.py`)**:
  - Arms an actual background process that monitors the system clock.
  - Automatically updates the Airflow DAG cron expression (`dags/retainiq_pipeline_dag.py`).
  - When the clock strikes the target minute, it automatically executes the end-to-end pipeline and sends real email alerts.
  - Automatically unarms upon completion and writes a `scheduler_completed.info` receipt (no stale "Armed" state).
* **Instant Automated Trigger**: Allows triggering a full automated pipeline cycle on demand in 3 seconds.
* **Enterprise Principles Display**: Zero code clutter; highlights deterministic scheduling, task isolation, and automatic retries.

### Tab 4: Live Gmail Alert Inspector
* Displays the active recipient list header.
* Features a 650px responsive HTML iframe preview of the exact email dispatched to leadership.

---

## 🔄 The Streamlit $\leftrightarrow$ Power BI Decoupled Data Contract

### How Does Power BI Update with One Click of "Refresh"?

```
┌────────────────────────┐      ┌───────────────────────────┐      ┌───────────────────────────┐
│   Streamlit Web App    │ ───> │  Python Pipeline & ML     │ ───> │ Export Clean CSV Views    │
│  "Simulate / Run" Btn  │      │  (DB Write + ML Scoring)  │      │ to data/processed/*.csv   │
└────────────────────────┘      └───────────────────────────┘      └─────────────┬─────────────┘
                                                                                 │
                                                                                 ▼
                                                                   ┌───────────────────────────┐
                                                                   │     Power BI Desktop      │
                                                                   │   Click "Refresh" Button  │
                                                                   │   (Instantly Reloads UI)  │
                                                                   └───────────────────────────┘
```

1. **Decoupled Architecture**: Instead of Power BI locking SQLite tables during write operations, Python exports denormalized analytical views (`v_daily_action_queue.csv`, `v_executive_kpis.csv`) to `data/processed/`.
2. **Fixed File Contracts**: The CSV schema and file paths never change.
3. **Instant Refresh**: When you click **Refresh** in Power BI, its VertiPaq engine re-reads the local CSVs from disk and re-renders all DAX measures in under 1 second with zero connection errors.

---

## 👥 Dynamic Alert Recipients Management (Sidebar)

* **Default Pre-Population**: Loads existing verified emails from `src/config.py`.
* **Interactive Editing**: Multi-line text field allowing adding, editing, or deleting stakeholder emails.
* **Optional CSV Ingestion**: File uploader to import employee emails from any `.csv` file and append them to the active recipient list.
* **Persistence**: Saves active recipients to `data/recipients.json`, shared across Airflow, the scheduled demo, and manual UI triggers.

---

## 🚀 How to Launch & Run the Operations Console

### 1. Standard Terminal Launch Command
Open your terminal (PowerShell, Command Prompt, or bash) in the project root directory (`d:\important_cmd_history\project fopr suretrust`):

```bash
# Recommended standard execution:
python -m streamlit run app.py --server.port 8501

# Or shorthand CLI syntax:
streamlit run app.py
```

### 2. Headless / Server Execution (No Auto-Browser Popup)
If running inside a script, background service, or remote server:
```bash
python -m streamlit run app.py --server.headless true --server.port 8501
```

### 3. Local Access URL
Once started, the console is instantly accessible in any web browser at:
```
Local URL: http://localhost:8501
Network URL: http://<your-local-ip>:8501
```

### 4. Prerequisites & Environment Setup
Before launching, ensure Python dependencies are installed:
```bash
# Optional: Activate your virtual environment (if using one)
# .\venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt
```

---

## 🧠 Core Architectural Defense Q&A

### Q1: Which Machine Learning model was selected, why, and what does the 0.86 ROC-AUC score signify for the business?
> **Answer:**
> *"We selected a **Tuned Random Forest Classifier** over Logistic Regression and Neural Networks for three distinct reasons:
> 1. **Complex Non-Linear Interactions**: In customer retention, churn is rarely caused by a single linear factor. A customer who has low tenure, recently filed a customer service complaint, and hasn't ordered in 30 days has a compounding risk of churn. Random Forest naturally captures multi-way feature interactions through recursive decision tree partitioning without requiring manual polynomial feature engineering.
> 2. **Robustness to Tabular Outliers & Imbalance**: Random Forest resists extreme values in monetary spend and tenure through bagging (bootstrap aggregating), preventing individual high-spend outliers from skewing decision boundaries.
> 3. **Explainability & Feature Importance**: In production, leadership demands to know *why* an account is flagged. Random Forest provides transparent Gini impurity feature importances (identifying Tenure, Complaints, and Recency as the top 3 drivers).
>
> **The 0.86 ROC-AUC Score:**
> While our raw classification accuracy is **81.8%**, accuracy is deceptive on imbalanced datasets (~14% baseline churn). **ROC-AUC (0.86)** measures the model's true discriminatory power across all possible decision thresholds.
> Mathematically, an ROC-AUC of 0.86 means that if we randomly choose one customer who actually churned and one who remained loyal, **there is an 86% probability that our model assigns a higher churn risk score to the churned customer**.
> In business terms, this guarantees high ranking fidelity: Customer Success teams will not waste time calling accounts that are actually happy, protecting retention teams from false-alarm alert fatigue."*

---

### Q2: Why was the High Alert Risk Threshold set at 80% rather than the standard 50% cutoff?
> **Answer:**
> *"Setting a classification cutoff at the standard 50% midpoint makes mathematical sense for symmetric problems, but **customer retention has an asymmetric economic cost structure**:
> 1. **Human Labor Costs ($)**: Having a Customer Success representative pick up the phone, review customer history, and conduct an intervention call costs significant time and company payroll.
> 2. **Retention Offer Dilution ($)**: Offering aggressive retention incentives (such as 20% loyalty discounts, free expedited shipping, or account credits) cuts directly into gross margins. Offering these incentives to customers who only had a 52% probability of leaving unnecessarily burns revenue on accounts that likely would have stayed anyway.
>
> By calibrating our high-alert threshold to **$\ge 80\%$**, we isolate the **urgent attrition crisis cohort** (~339 accounts out of 5,630). 
> - **Accounts $\ge 80\%$ (Crisis Tier)**: Receive immediate human sales intervention and trigger the daily automated Gmail OAuth priority alert dispatched to leadership.
> - **Accounts between 50% and 79% (At-Risk Tier)**: Are automatically assigned to passive, low-cost digital nurturing campaigns (automated product recommendation newsletters).
> This ensures company resources are deployed where the expected return on retention spend is maximized."*

---

### Q3: What is Behavioral RFM Segmentation and how were the 11 personas engineered?
> **Answer:**
> *"**RFM** is the gold-standard behavioral segmentation framework in e-commerce:
> - **Recency (R)**: Days since the customer's last order (`day_since_last_order`). Lower recency indicates strong current brand engagement.
> - **Frequency (F)**: Total number of orders placed over the customer's lifetime. Differentiates one-time buyers from habitual repeat shoppers.
> - **Monetary (M)**: Total lifetime spend and monetary contribution (represented by order spend and `cashback_amount`).
>
> **Engineering the 11 Personas:**
> Rather than arbitrary hardcoded cutoffs, we applied **statistical quintile ranking** using `pd.qcut()`. Customers receive a relative score from 1 (worst) to 5 (best) across each dimension:
> - `R_Score` (1 to 5; with 5 being the most recent buyers).
> - `F_Score` (1 to 5; with 5 having the highest order count).
> - `M_Score` (1 to 5; with 5 having the highest spend).
>
> By concatenating and evaluating these scores, we map each customer into one of **11 strategic business personas**:
> 1. **Champions** (R: 4-5, F: 4-5, M: 4-5): Best customers, buy frequently and spend heavily.
> 2. **Loyal Customers** (R: 3-5, F: 3-5, M: 3-5): Steady, responsive buyers with consistent revenue.
> 3. **Potential Loyalists** (R: 4-5, F: 2-3, M: 2-3): Recent buyers with moderate spend; candidates for loyalty programs.
> 4. **Promising** (R: 3-4, F: 1-2, M: 1-2): Recent buyers who haven't built strong frequency yet.
> 5. **New Customers** (R: 4-5, F: 1, M: 1): High recency, but brand new. Need onboarding touchpoints.
> 6. **Need Attention** (R: 2-3, F: 2-3, M: 2-3): Average frequency and recency; vulnerable if ignored.
> 7. **About to Sleep** (R: 2-3, F: 1-2, M: 1-2): Below-average activity; will churn without re-engagement.
> 8. **At Risk** (R: 1-2, F: 3-5, M: 3-5): Spent big money in the past, but haven't returned recently. **High priority**.
> 9. **Can't Lose Them** (R: 1-2, F: 4-5, M: 4-5): Historical top-tier spenders showing severe inactivity. Immediate outreach required.
> 10. **Hibernating** (R: 1-2, F: 1-2, M: 1-2): Low spenders who have been gone for a long time.
> 11. **Lost** (R: 1, F: 1, M: 1): Lowest scores across all 3 dimensions. Lowest ROI for recovery.
>
> This segmentation provides critical behavioral signals to our Random Forest model and allows customer outreach to be personalized rather than generic."*

---

### Q4: How does Apache Airflow automate and orchestrate the enterprise pipeline?
> **Answer:**
> *"In production, machine learning models should never rely on someone manually running a Jupyter notebook. **Apache Airflow** provides autonomous, production-grade scheduling and orchestration:
> 1. **Deterministic Cron Scheduling**: Our DAG (`dags/retainiq_pipeline_dag.py`) is scheduled to run autonomously at `0 6 * * *` (every morning at 6:00 AM UTC/local), ensuring executive dashboards and sales queues are refreshed before business hours begin.
> 2. **Modern TaskFlow API**: Built using Airflow 2.x Python decorators (`@dag`, `@task`), creating clean, maintainable, self-documenting code.
> 3. **Strict Task Isolation & Execution Flow**:
>    ```
>    ingest_raw_data >> feature_engineering_rfm >> ml_inference_scoring >> export_powerbi_views >> dispatch_gmail_alerts
>    ```
> 4. **Enterprise Resilience & Error Handling**: If the database lock fails or an API times out, Airflow automatically pauses downstream tasks, initiates up to 3 retries with exponential backoff, and logs error stack traces to disk.
> 5. **Database Pushdown Pattern**: Tasks do not pass bulky 5,600-row DataFrames across XComs (which bloats Airflow's metadata database). Instead, tasks push heavy data into SQLite/Parquet and pass only lightweight operational metadata (row counts, churn rates, email message IDs) through XComs."*

---

### Q5: How does Power BI update in one second when a simulation is triggered in Streamlit?
> **Answer:**
> *"This instantaneous refresh is achieved through a **Decoupled Analytical Data Contract**:
> 1. **The Common Mistake**: Novice data projects connect Power BI directly to the active SQLite/PostgreSQL transaction tables via ODBC. When a Python script writes 35 new rows, it locks the database table. If Power BI attempts to read during the write, it results in deadlocks, timeout errors, or frozen dashboards.
> 2. **Our Decoupled Solution**:
>    - When you click **'Simulate Incoming Batch'** in Streamlit, the Python backend writes the new transactions to SQL, recalculates RFM quintiles, runs Random Forest inference, and **immediately exports two pre-aggregated analytical CSV views**:
>      - `data/processed/v_daily_action_queue.csv`
>      - `data/processed/v_executive_kpis.csv`
>    - Power BI Desktop is configured with Power Query pointing directly to these deterministic local CSV contracts.
> 3. **The VertiPaq Engine**:
>    - When you click **Refresh** in Power BI, its internal **VertiPaq columnar in-memory database engine** reads the flat CSV files from disk directly into local RAM.
>    - Because the analytical calculations (RFM logic, risk probability brackets, tenure buckets) were already pre-computed upstream by Python in SQL, Power BI doesn't need to do any heavy joins or transformations.
>    - The VertiPaq engine recalculates all DAX measures and re-renders all visual cards in under 1 second without a single database contention lock."*

---

## 🎙️ Live Demo Evaluator Q&A

### Q6: Why did you choose Streamlit instead of building a React/Node.js or Django web application?
> **Answer:**
> *"For operational machine learning platforms, time-to-value and architectural cohesion are paramount:
> 1. **Native Python Data Ecosystem**: Streamlit runs inside the same Python runtime as Pandas, Scikit-Learn, and the Google API client. Building in React would require scaffolding a REST/FastAPI backend, serialization/deserialization layers, CORS management, and state syncing libraries.
> 2. **Engineering Efficiency**: Building in Streamlit allowed 95% of our engineering effort to be dedicated to data engineering, statistical modeling, and pipeline resilience rather than managing frontend CSS or JavaScript build tools.
> 3. **Executive Reactive UI**: Streamlit's reactive reruns ensure that when a user filters by threshold or updates recipient emails, the entire interface immediately reflects the new state with zero frontend latency."*

---

### Q7: How does the recipient management system handle invalid or malicious email inputs?
> **Answer:**
> *"The dynamic recipient manager implements strict defensive input validation:
> 1. **RFC 5322 Regex Parsing**: Each entered email address is validated against standard RFC email patterns (`r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'`).
> 2. **Deduplication & Sanitization**: Whitespace, newlines, and trailing commas are stripped, and addresses are deduplicated using Python sets.
> 3. **Administrative Fallback Protection**: If a user clears all email fields or submits invalid text, the system protects against silent delivery failure by falling back to the verified baseline administrative recipients defined in `src/config.py` (`ALERT_RECIPIENT_EMAILS`)."*

---

### Q8: What happens to the Background Scheduler if someone closes the browser tab during a countdown?
> **Answer:**
> *"The scheduler does **not** break or terminate when the browser tab is closed.
> We engineered `scripts/schedule_demo.py` to run as an independent, detached **operating system background process** (`subprocess.Popen`).
> It does not execute within the browser's JavaScript event loop or the Streamlit WebSocket connection. Once armed, the Python daemon runs directly on the host machine, independently monitoring the system clock. Even if the user closes their browser, closes Streamlit, or locks the workstation, the daemon executes the pipeline, updates Airflow cron schedules, dispatches the Gmail alerts, writes the completion log (`data/scheduler_completed.info`), and terminates cleanly."*

---

### Q9: How would this Streamlit Operations Hub scale if the business expands to 100,000+ accounts?
> **Answer:**
> *"We designed the system with modular architectural tiers that scale gracefully:
> 1. **Data Layer**: SQLite would be migrated to **PostgreSQL, Snowflake, or Google BigQuery**, leveraging indexed partitioning on `customer_id` and `order_date`.
> 2. **Compute & Inference**: Model inference would be decoupled from the web server. Instead of running `predict_proba` inside the Streamlit process, the UI would publish a job message to an **Apache Airflow / Celery task queue**, which executes distributed batch inference across worker nodes.
> 3. **UI Caching & Pagination**:
>    - Apply Streamlit's `@st.cache_data(ttl=3600)` with memoization to store aggregated KPIs in server memory.
>    - Implement **server-side SQL pagination (`LIMIT` / `OFFSET`)** on the High-Risk Action Queue table so the browser only renders 50 customer rows at a time rather than trying to mount 100,000 rows into the DOM."*

