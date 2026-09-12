# 🎯 Stage 7: Master Interview & Project Defense Q&A

> **Voice Mode Explainer:**
> Use this document for rapid oral interview prep. You can prompt Gemini Voice: *"Ask me question 1 and listen to my answer, then give me feedback."*

---

## 🏢 Business & Strategy

### Q1: What makes RetainIQ different from typical student churn projects?
> **Answer:** *"Most churn projects end with a static Jupyter Notebook and an accuracy score. RetainIQ is an end-to-end operational engine. It doesn't just predict churn; it automates daily business workflows. It uses Airflow to orchestrate daily data ingestion, computes RFM loyalty scores in Pandas, predicts risk probabilities via Random Forest, dispatches automated Gmail OAuth alerts for accounts exceeding 80% risk, and surfaces an interactive 1-page action queue in Power BI."*

### Q2: Why focus on retention over acquiring new customers?
> **Answer:** *"Acquiring a new customer costs 5 to 7 times more than retaining an existing one. Furthermore, research shows that a 5% increase in retention can boost overall company profits by 25% to 95% because existing customers have higher average order values and zero acquisition overhead."*

---

## 🗄️ Data Engineering & SQL

### Q3: Why did you compute RFM metrics in Task 2 instead of just feeding raw columns into the model?
> **Answer:** *"Raw numbers like '10 orders' lack temporal context. A customer who ordered 10 times two years ago is completely different from someone who ordered 10 times this week. RFM quintile analysis (1–5) captures relative customer velocity across Recency, Frequency, and Monetary dimensions. It segments users into tiers like Champions, Loyalists, and At-Risk, providing crucial predictive signals to our Random Forest model."*

### Q4: Why create SQL analytical views (`v_daily_action_queue`) instead of doing transformations inside Power BI?
> **Answer:** *"In production data architectures, business logic should live as close to the data source as possible. By pushing heavy joins and aggregations into SQL views, the database engine computes the results using indexes. This minimizes network transfer and allows Power BI to render interactive dashboards with sub-second latency."*

---

## 🌲 Machine Learning & Statistics

### Q5: Why did you choose Random Forest over Logistic Regression or Deep Learning?
> **Answer:** *"For tabular customer data with 5,600+ rows, tree-based ensembles consistently outperform single linear models and neural networks. Random Forest naturally captures complex non-linear feature interactions (such as low tenure combined with open complaints), requires minimal feature scaling, resists overfitting via bagging, and produces well-calibrated continuous probability outputs."*

### Q6: Why optimize for Recall instead of Accuracy or Precision?
> **Answer:** *"In churn prediction, datasets are imbalanced (~14% churn). A naive model predicting 'No Churn' for everyone achieves 86% accuracy while catching zero churners! In our business context, a False Negative (missing a leaving customer) loses hundreds of dollars in lifetime value. A False Positive (offering a small retention discount to a loyal customer) has minimal cost. Therefore, we tuned class weights and thresholds specifically to maximize Recall."*

### Q7: What is the role of `predict_proba()` in your pipeline?
> **Answer:** *"Standard `predict()` only returns binary 0 or 1 labels. In contrast, `predict_proba()` calculates the continuous probability from 0% to 100%. We use this continuous risk to assign dynamic risk tiers (High for $\ge 80\%$, Medium for $50-79\%$, Low for $< 50\%$). The 80% threshold specifically triggers the automated daily email alerts to ensure sales managers only receive high-priority, high-confidence intervention targets."*

---

## 🌪️ Apache Airflow & Pipeline Orchestration

### Q8: What is the advantage of using Apache Airflow over a simple Python script?
> **Answer:** *"Airflow provides strict task isolation, deterministic scheduling, automatic retries, execution logging, and dependency management. In our 4-task DAG (`Ingest >> RFM >> Infer >> Alert`), if Task 1 fails due to a database connection timeout, Airflow pauses the pipeline, retries after 5 minutes, and prevents downstream inference from running on corrupted or empty data."*

### Q9: How do tasks pass data between each other in your Airflow DAG? Do you pass DataFrames through XComs?
> **Answer:** *"Never pass large DataFrames through XComs. In RetainIQ, we implemented the Database Pushdown Pattern: heavy data (5,630 customer records and RFM scores) is written directly into the SQL database or Parquet storage. Airflow's TaskFlow API uses XComs strictly for lightweight operational metadata—such as row counts, churn percentages, and Gmail dispatch message IDs for audit logging."*

### Q10: How does Airflow run on your local machine versus a production cluster?
> **Answer:** *"Airflow is natively designed for Linux environments on Docker/Kubernetes with Celery or Kubernetes executors. In our repository, `dags/retainiq_pipeline_dag.py` uses modern Airflow 2.x TaskFlow decorators (`@dag`, `@task`). For local Windows development and instant demo defense, we built a dual-mode compatibility shim so the pipeline runs in under 3 seconds via `run_pipeline.py` with 100% functional parity with an Airflow executor."*

---

## 📊 Power BI & Visualization

### Q11: Why did you design the Power BI dashboard as a 1-page "Control Tower" instead of multiple tabs?
> **Answer:** *"To prevent cognitive overload for executive leadership. We implemented a 1-page 'Single-Pane-of-Glass' design following a strict 3-tier visual hierarchy: Row 1 gives high-level portfolio KPIs (5,630 accounts, 86.3% retention, 339 high-risk), Row 2 diagnoses root causes (category churn and 70-month tenure decay curve), and Row 3 provides an unsummarized daily tactical action queue sorted by highest churn risk."*

### Q12: Why did you push data aggregations into SQL Views (`v_executive_kpis`, `v_daily_action_queue`) instead of doing them in Power Query?
> **Answer:** *"In enterprise data architectures, the standard practice is 'Transform upstream, visualize downstream.' By executing window functions, RFM case logic, and joins inside SQL views on the database engine, we leverage database indexing and query optimization. This keeps the Power BI data model lightweight and allows instant 1-click refreshes with zero report lag."*

### Q13: How does your system demonstrate live, dynamic batch updates in Power BI without corrupting historical baselines?
> **Answer:** *"We engineered an incremental simulation mode alongside a 1-click reset switch. Running `python run_pipeline.py --simulate` appends 35 realistic incoming customer transactions and complaints to SQL, recalibrates RFM, scores the new cohort, sends an email alert, and exports fresh CSV views. When we click Refresh in Power BI, mentors watch the KPI cards live-tick from 5,630 to 5,665! Furthermore, passing `--reset` wipes the simulation batch and restores the exact 5,630 baseline in 2.4 seconds."*

---

## 🔐 Security & APIs

### Q14: Why did you use Gmail OAuth 2.0 instead of plain SMTP with passwords?
> **Answer:** *"Hardcoding email passwords in source code violates security standards and risks credential leaks in version control. Gmail OAuth 2.0 uses secure, token-based authentication. The application uses client secrets (`credentials.json`) to obtain a scoped, revocable access token (`token.json`). The code only requests the minimal required scope (`gmail.send`), ensuring enterprise-grade credential safety."*

---

## 🧬 Scalability & Quality Assurance

### Q15: How did you verify the integrity and reliability of the entire system?
> **Answer:** *"We built an automated end-to-end integration test suite in `tests/test_pipeline_e2e.py` covering all 5 phases: database schema creation, CSV ingestion, RFM feature engineering, Random Forest inference, alert audit logging, and Power BI CSV dataset exports. All 7 tests pass in 4.10 seconds with 100% pass rate, ensuring regression-free execution."*
