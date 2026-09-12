#!/usr/bin/env python3
"""
RetainIQ: Customer Intelligence Engine - Master Pipeline Runner
Executes the full 5-stage automated workflow:
  Task 1: SQL Data Ingestion (Pulls raw customer accounts into SQL)
  Task 2: RFM Feature Engineering (Computes Recency, Frequency, Monetary via Pandas)
  Task 3: Scikit-Learn Model Inference & Risk Scoring (0 to 100% risk)
  Task 4: High-Risk Alert Emailing & Audit Trail (Dispatches HTML report for >80% risk)
  Task 5: Power BI Analytical Views & Automated CSV Export (Ready for 1-click import)

Modes Supported:
  - Standard Run:         python run_pipeline.py            (Baseline: 5,630 accounts)
  - Live Demo Simulation: python run_pipeline.py --simulate (Adds 35 incoming accounts for live Power BI refresh)
  - Instant Reset Switch: python run_pipeline.py --reset    (Restores pristine 5,630 baseline)
"""

import sys
import time
import logging
import argparse
from datetime import datetime, timezone
import pandas as pd

# Configure UTF-8 output encoding for Windows compatibility
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from src.config import PROCESSED_DATA_DIR
from src.db.connection import get_engine
from src.db.schema import init_db
from src.etl.ingest import ingest_raw_data
from src.etl.feature_engineering import engineer_features
from src.ml.inference import predict_churn_risk
from src.alerts.gmail_alert import send_churn_alerts

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("RetainIQ-Runner")

def export_powerbi_datasets(engine) -> dict:
    """
    Exports analytical SQL views and core tables to CSV files
    in data/processed/ for seamless, instant import into Power BI Desktop.
    """
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    datasets = {
        "v_daily_action_queue": "SELECT * FROM v_daily_action_queue",
        "v_executive_kpis": "SELECT * FROM v_executive_kpis",
        "v_churn_drivers": "SELECT * FROM v_churn_drivers",
        "v_rfm_matrix": "SELECT * FROM v_rfm_matrix",
        "churn_predictions": "SELECT * FROM churn_predictions",
        "raw_customers": "SELECT customer_id, tenure, city_tier, preferred_payment_mode, prefered_order_cat, satisfaction_score, complain, order_count, day_since_last_order, cashback_amount, churn FROM raw_customers"
    }

    exported_files = []
    for name, sql in datasets.items():
        out_csv = PROCESSED_DATA_DIR / f"{name}.csv"
        df = pd.read_sql(sql, con=engine)
        df.to_csv(out_csv, index=False)
        exported_files.append((name, len(df), str(out_csv)))

    return {
        "status": "SUCCESS",
        "exported_count": len(exported_files),
        "files": exported_files
    }

def run_full_pipeline(mode: str = "baseline", batch_size: int = 35):
    start_time = time.time()
    mode_label = " [MODE: LIVE DEMO SIMULATION (+" + str(batch_size) + " ACCOUNTS)]" if mode == "simulate" else (" [MODE: RESET TO BASELINE]" if mode == "reset" else " [MODE: BASELINE RUN]")
    print("\n" + "="*70)
    print(f" [*] RETAINIQ: CUSTOMER INTELLIGENCE ENGINE{mode_label}")
    print("="*70)
    print(f" Started at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("="*70 + "\n")

    engine = get_engine()

    # -------------------------------------------------------------
    # Initialization: Ensure Schemas & Analytical Views Exist
    # -------------------------------------------------------------
    init_db(engine=engine)

    # -------------------------------------------------------------
    # Task 1: Ingestion
    # -------------------------------------------------------------
    print(" [1/5] Executing Task 1: SQL Data Ingestion...")
    t1_res = ingest_raw_data(engine=engine, mode=mode, batch_size=batch_size)
    if mode == "simulate":
        print(f"       [+] Simulation Ingested: {t1_res['new_records']} incoming accounts.")
        print(f"       [+] Total Database Volume: {t1_res['total_records']} customer records.")
    else:
        print(f"       [+] Ingestion Complete: {t1_res['total_records']} customer records written to SQL.")
    print(f"           Portfolio Churn Rate: {t1_res['churn_rate_pct']}%\n")

    # -------------------------------------------------------------
    # Task 2: Feature Engineering
    # -------------------------------------------------------------
    print(" [2/5] Executing Task 2: RFM Feature Engineering (Pandas)...")
    t2_res = engineer_features(engine=engine)
    print(f"       [+] RFM Complete: {t2_res['total_records_processed']} customer profiles scored.")
    print(f"           Segments: {t2_res['rfm_segments_count']}\n")

    # -------------------------------------------------------------
    # Task 3: Model Inference
    # -------------------------------------------------------------
    print(" [3/5] Executing Task 3: Model Inference & Churn Risk Prediction...")
    t3_res = predict_churn_risk(engine=engine)
    print(f"       [+] Inference Complete: {t3_res['total_scored']} customers scored.")
    print(f"           Risk Breakdown -> High (>80%): {t3_res['high_risk_count']} | Medium: {t3_res['medium_risk_count']} | Low: {t3_res['low_risk_count']}")
    print(f"           Average Portfolio Risk: {t3_res['avg_risk_pct']}%\n")

    # -------------------------------------------------------------
    # Task 4: Email Action
    # -------------------------------------------------------------
    print(" [4/5] Executing Task 4: Automated High-Risk Churn Alerting...")
    t4_res = send_churn_alerts(engine=engine)
    print(f"       [+] Alert Status: {t4_res['status']}")
    print(f"           Target Accounts (>80%): {t4_res['total_high_risk_flagged']}")
    print(f"           Details: {t4_res['details']}\n")

    # -------------------------------------------------------------
    # Task 5: Power BI Data Export
    # -------------------------------------------------------------
    print(" [5/5] Executing Task 5: Power BI Analytical Views & CSV Export...")
    t5_res = export_powerbi_datasets(engine=engine)
    print(f"       [+] Export Complete: {t5_res['exported_count']} datasets exported to data/processed/.")
    print("           - v_daily_action_queue.csv (Top operational queue for support teams)")
    print("           - v_executive_kpis.csv     (Executive KPI cards: Churn %, Retention %)")
    print("           - v_churn_drivers.csv      (Behavioral diagnostics by category & tenure)")
    print("           - v_rfm_matrix.csv         (Loyalty quintiles & segment risk)\n")

    elapsed = round(time.time() - start_time, 2)
    print("="*70)
    if mode == "reset":
        print(f" [SUCCESS] DATABASE RESET COMPLETE in {elapsed}s")
        print(" Database restored to pristine baseline (5,630 customers, 339 high-risk).")
    elif mode == "simulate":
        print(f" [SUCCESS] DYNAMIC BATCH SIMULATION COMPLETE in {elapsed}s")
        print(f" Ingested {batch_size} new accounts. Power BI is ready for 1-click refresh!")
    else:
        print(f" [SUCCESS] PIPELINE COMPLETED in {elapsed}s")
        print(" All database tables and Power BI datasets are refreshed and ready.")
    print("="*70 + "\n")

    return {
        "task1": t1_res,
        "task2": t2_res,
        "task3": t3_res,
        "task4": t4_res,
        "task5": t5_res,
        "elapsed_seconds": elapsed
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RetainIQ: Master Pipeline Runner")
    parser.add_argument("--simulate", action="store_true", help="Simulate an incoming daily batch of customer accounts")
    parser.add_argument("--batch", type=int, default=35, help="Number of incoming accounts to simulate (default: 35)")
    parser.add_argument("--reset", action="store_true", help="Reset database back to the pristine 5,630 customer baseline")
    args = parser.parse_args()

    pipeline_mode = "baseline"
    if args.reset:
        pipeline_mode = "reset"
    elif args.simulate:
        pipeline_mode = "simulate"

    run_full_pipeline(mode=pipeline_mode, batch_size=args.batch)
