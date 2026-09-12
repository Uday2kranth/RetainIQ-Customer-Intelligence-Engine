"""
SKELETON CODE: Stage 5 - Apache Airflow DAG Orchestration
File Reference: dags/retainiq_pipeline_dag.py
"""
from datetime import datetime, timedelta
from airflow.decorators import dag, task
from src.etl.ingest import ingest_raw_data
from src.etl.feature_engineering import compute_rfm_features
from src.ml.inference import run_batch_inference
from src.alerts.gmail_alert import send_churn_alerts

default_args = {
    "owner": "retainiq_analytics",
    "retries": 2,                           # Retry up to 2 times on failure
    "retry_delay": timedelta(minutes=5),    # Wait 5 minutes between retries
}

@dag(
    dag_id="retainiq_daily_customer_intelligence_pipeline",
    default_args=default_args,
    schedule="@daily",                      # Scheduled every 24 hours at 06:00 UTC
    start_date=datetime(2026, 1, 1),
    catchup=False
)
def retainiq_dag():
    @task(task_id="task_1_sql_ingestion")
    def task_ingest() -> dict:
        return ingest_raw_data()

    @task(task_id="task_2_rfm_feature_engineering")
    def task_rfm(ingest_meta: dict) -> dict:
        return compute_rfm_features()

    @task(task_id="task_3_model_inference")
    def task_infer(rfm_meta: dict) -> dict:
        return run_batch_inference()

    @task(task_id="task_4_gmail_alert_action")
    def task_alert(infer_meta: dict) -> dict:
        return send_churn_alerts()

    # Enforce strict 1-way workflow dependencies:
    ingest_meta = task_ingest()
    rfm_meta = task_rfm(ingest_meta)
    infer_meta = task_infer(rfm_meta)
    task_alert(infer_meta)

# Instantiate the DAG
pipeline = retainiq_dag()
