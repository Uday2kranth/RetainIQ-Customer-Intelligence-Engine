"""
===============================================================================
RetainIQ: Customer Intelligence Engine - Apache Airflow Production DAG
===============================================================================
Automates the daily 4-stage operational retention pipeline:
  Task 1: SQL Data Ingestion (Pulls fresh customer records into SQL)
  Task 2: RFM Feature Engineering (Computes Recency, Frequency, Monetary via Pandas)
  Task 3: Model Inference (Predicts churn probabilities via churn_model.pkl & updates SQL)
  Task 4: Email Action (Dispatches automated HTML alerts for >80% risk accounts via Gmail OAuth)
===============================================================================
"""

import os
import sys
from datetime import datetime, timedelta

# Ensure project root is available in sys.path when executed inside Airflow
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from airflow.decorators import dag, task
    AIRFLOW_AVAILABLE = True
except ImportError:
    AIRFLOW_AVAILABLE = False
    # Mock decorators for environments where airflow is imported outside its scheduler
    def dag(*args, **kwargs):
        def decorator(f):
            return f
        return decorator

    def task(*args, **kwargs):
        def decorator(f):
            return f
        return decorator

from src.db.connection import get_engine
from src.etl.ingest import ingest_raw_data
from src.etl.feature_engineering import engineer_features
from src.ml.inference import predict_churn_risk
from src.alerts.gmail_alert import send_churn_alerts

default_args = {
    "owner": "retainiq_analytics",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

@dag(
    dag_id="retainiq_daily_customer_intelligence_pipeline",
    default_args=default_args,
    description="Automated Daily Churn Prediction & Action Alerting Pipeline (RetainIQ)",
    schedule="35 21 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["ecommerce", "churn_prediction", "mlops", "retainiq"]
)
def retainiq_pipeline():
    """
    RetainIQ End-to-End Orchestrated Pipeline.
    Linear Workflow: Ingestion >> Feature Engineering >> Model Inference >> Action Alert
    """

    @task(task_id="task_1_sql_ingestion")
    def task_ingest() -> dict:
        """Pulls fresh customer accounts and updates the raw_customers SQL table."""
        engine = get_engine()
        result = ingest_raw_data(engine=engine)
        return result

    @task(task_id="task_2_rfm_feature_engineering")
    def task_rfm(ingestion_metadata: dict) -> dict:
        """Calculates Recency, Frequency, Monetary (RFM) quintiles & customer segments."""
        engine = get_engine()
        result = engineer_features(engine=engine)
        return result

    @task(task_id="task_3_model_inference")
    def task_inference(rfm_metadata: dict) -> dict:
        """Loads churn_model.pkl, predicts churn risk (%), and updates SQL prediction tables."""
        engine = get_engine()
        result = predict_churn_risk(engine=engine)
        return result

    @task(task_id="task_4_gmail_alert_action")
    def task_alert(inference_metadata: dict) -> dict:
        """Identifies >80% high-risk customers and triggers automated Gmail alert emails."""
        engine = get_engine()
        result = send_churn_alerts(engine=engine)
        return result

    # Define Linear Execution Flow
    ingest_res = task_ingest()
    rfm_res = task_rfm(ingest_res)
    infer_res = task_inference(rfm_res)
    alert_res = task_alert(infer_res)

# Instantiate the DAG
retainiq_dag = retainiq_pipeline()
