"""
===============================================================================
RetainIQ: End-to-End Automated Integration Test Suite
===============================================================================
Validates:
  1. Database initialization and table DDL schemas.
  2. Task 1: Ingestion of 5,600+ customer records into SQL.
  3. Task 2: RFM Feature Engineering and behavioral segmentation.
  4. Task 3: Random Forest model training, serialization, and inference.
  5. Task 4: High-risk alerting, HTML generation, and alert history logging.
  6. Power BI SQL views execution and consistency.
===============================================================================
"""

import os
import sys
import unittest
import pandas as pd
from sqlalchemy import text

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.db.connection import get_engine
from src.db.schema import init_db
from src.etl.ingest import ingest_raw_data
from src.etl.feature_engineering import engineer_features
from src.ml.train import train_churn_model
from src.ml.inference import predict_churn_risk
from src.alerts.gmail_alert import send_churn_alerts
from src.config import MODEL_PATH, PROCESSED_DATA_PATH, DATA_DIR

class TestRetainIQPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up test environment and initialize database engine."""
        cls.engine = get_engine()
        init_db(cls.engine)

    def test_01_database_init(self):
        """Verify database tables are created."""
        with self.engine.connect() as conn:
            # Query tables
            tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", con=conn)
            table_names = tables["name"].tolist()
            self.assertIn("raw_customers", table_names)
            self.assertIn("rfm_features", table_names)
            self.assertIn("churn_predictions", table_names)
            self.assertIn("alert_history", table_names)

    def test_02_task1_ingestion(self):
        """Verify Task 1: Data Ingestion into SQL."""
        res = ingest_raw_data(engine=self.engine)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertGreaterEqual(res["total_records"], 5000)

        df = pd.read_sql("SELECT * FROM raw_customers", con=self.engine)
        self.assertFalse(df.empty)
        self.assertIn("customer_id", df.columns)
        self.assertIn("churn", df.columns)
        self.assertIn("tenure", df.columns)
        self.assertIn("complain", df.columns)

    def test_03_task2_rfm_feature_engineering(self):
        """Verify Task 2: RFM Feature Engineering."""
        res = engineer_features(engine=self.engine)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertGreaterEqual(res["total_records_processed"], 5000)

        rfm_df = pd.read_sql("SELECT * FROM rfm_features", con=self.engine)
        self.assertFalse(rfm_df.empty)
        self.assertIn("recency_days", rfm_df.columns)
        self.assertIn("frequency_orders", rfm_df.columns)
        self.assertIn("monetary_cashback", rfm_df.columns)
        self.assertIn("rfm_segment", rfm_df.columns)

    def test_04_task3_model_inference(self):
        """Verify Task 3: Scikit-Learn Model Training & Inference."""
        if not os.path.exists(MODEL_PATH):
            train_res = train_churn_model()
            self.assertIn("roc_auc", train_res)
            self.assertGreaterEqual(train_res["roc_auc"], 0.65)

        infer_res = predict_churn_risk(engine=self.engine)
        self.assertEqual(infer_res["status"], "SUCCESS")
        self.assertGreater(infer_res["total_scored"], 0)
        self.assertGreater(infer_res["high_risk_count"], 0)

        pred_df = pd.read_sql("SELECT * FROM churn_predictions", con=self.engine)
        self.assertFalse(pred_df.empty)
        self.assertIn("churn_risk_pct", pred_df.columns)
        self.assertIn("risk_tier", pred_df.columns)

    def test_05_task4_alert_generation(self):
        """Verify Task 4: High-Risk Alert Generation & History Logging."""
        alert_res = send_churn_alerts(engine=self.engine)
        self.assertIn(alert_res["status"], ["SENT", "MOCKED"])
        self.assertGreater(alert_res["total_high_risk_flagged"], 0)

        # Check HTML file was written
        html_path = DATA_DIR / "latest_alert_email.html"
        self.assertTrue(os.path.exists(html_path))

        # Check SQL alert history
        history_df = pd.read_sql("SELECT * FROM alert_history", con=self.engine)
        self.assertFalse(history_df.empty)

    def test_06_powerbi_views(self):
        """Verify that Power BI SQL Views can be created and queried without error."""
        views_path = os.path.join(os.path.dirname(__file__), "..", "powerbi", "powerbi_views.sql")
        with open(views_path, "r", encoding="utf-8") as f:
            sql_script = f.read()

        with self.engine.connect() as conn:
            # Execute individual view statements
            for stmt in sql_script.split(";"):
                stmt = stmt.strip()
                if stmt:
                    conn.execute(text(stmt))
            conn.commit()

        # Query each view
        exec_kpis = pd.read_sql("SELECT * FROM v_executive_kpis", con=self.engine)
        self.assertFalse(exec_kpis.empty)
        self.assertIn("total_customers", exec_kpis.columns)

        action_queue = pd.read_sql("SELECT * FROM v_daily_action_queue LIMIT 10", con=self.engine)
        self.assertFalse(action_queue.empty)
        self.assertIn("recommended_action", action_queue.columns)

    def test_07_powerbi_csv_exports(self):
        """Verify that Power BI CSV datasets are exported properly and non-empty."""
        from run_pipeline import export_powerbi_datasets
        from src.config import PROCESSED_DATA_DIR

        export_res = export_powerbi_datasets(self.engine)
        self.assertEqual(export_res["status"], "SUCCESS")
        self.assertGreaterEqual(export_res["exported_count"], 4)

        queue_csv = PROCESSED_DATA_DIR / "v_daily_action_queue.csv"
        kpi_csv = PROCESSED_DATA_DIR / "v_executive_kpis.csv"
        self.assertTrue(queue_csv.exists())
        self.assertTrue(kpi_csv.exists())

        q_df = pd.read_csv(queue_csv)
        self.assertFalse(q_df.empty)
        self.assertIn("customer_id", q_df.columns)
        self.assertIn("recommended_action", q_df.columns)

if __name__ == "__main__":
    unittest.main(verbosity=2)

