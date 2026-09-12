# 🔗 Phase 4 User Guide: End-to-End Integration & System Verification

This guide explains how all subsystems of **RetainIQ** integrate together, how to run automated verification, how to set up real Gmail OAuth 2.0 credentials, and how to verify data flow into Power BI.

---

## 🏗️ System Integration Architecture

```
                                [ Kaggle Dataset (~5,630 Records) ]
                                                │
                                                ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                               APACHE AIRFLOW PIPELINE RUNNER                                     │
│                                                                                                  │
│   [Task 1: Ingest] ──▶ [Task 2: RFM Engine] ──▶ [Task 3: Model Inference] ──▶ [Task 4: Alert]   │
└──────────┬──────────────────────┬────────────────────────┬───────────────────────────┬───────────┘
           │                      │                        │                           │
           ▼                      ▼                        ▼                           ▼
    [raw_customers]        [rfm_features]        [churn_predictions]           [alert_history]
    ┌────────────────────────────────────────────────────────────────────────────────────────┐
    │                                  SQL DATABASE ENGINE                                   │
    └──────────────────────────────────────────┬─────────────────────────────────────────────┘
                                               │
                                               ▼
                              [ Power BI Control Tower Dashboard ]
                              - Executive KPI Cards
                              - Retention & Churn Drivers
                              - Daily High-Risk Action Queue
```

---

## 🧪 1. Running the Automated Integration Test Suite

The project includes an end-to-end test suite in `tests/test_pipeline_e2e.py` that verifies all 6 critical integration points:
1. Database initialization and table creation.
2. Ingestion of 5,600+ records.
3. RFM score generation and segmentation.
4. Random Forest model prediction & risk scoring.
5. High-risk alert filtering (>80%) and HTML report generation.
6. SQL analytical views execution for Power BI.

Run the test suite from your terminal:
```bash
python tests/test_pipeline_e2e.py
```
*Expected Result*:
```
Ran 6 tests in 1.36s
OK
```

---

## ✉️ 2. Setting Up Real Gmail OAuth 2.0 (Step-by-Step)

If you wish to send live emails to your real inbox:

1. **Get your Client Secret from Google Cloud**:
   * Go to [Google Cloud Console](https://console.cloud.google.com/).
   * Create a project (e.g. `RetainIQ-Alerts`).
   * Enable the **Gmail API** under *APIs & Services* ➔ *Library*.
   * Under *APIs & Services* ➔ *Credentials*, click **Create Credentials** ➔ **OAuth client ID**.
   * Application type: **Desktop app**.
   * Click **Download JSON** and save the downloaded file as `credentials.json` in your project root:
     `d:\important_cmd_history\project fopr suretrust\credentials.json`

2. **Run the Alert Script to Generate `token.json`**:
   ```bash
   python src/alerts/gmail_alert.py
   ```
   * A browser window will automatically open asking you to sign in with your Google account and grant send permission.
   * Click **Allow**.
   * A `token.json` file will be generated in your project root. Future executions will run completely autonomously in the background without opening a browser window.

3. **Check Your Inbox**:
   * You will receive a rich HTML email formatted with the daily high-risk customer queue.

---

## 🔄 3. Live End-to-End Execution Checklist

Follow this quick checklist whenever you want to demonstrate the completed project:

1. **Step 1**: Run the master pipeline to refresh the database with fresh predictions:
   ```bash
   python run_pipeline.py
   ```
2. **Step 2**: Open `data/latest_alert_email.html` in your browser to inspect the generated high-risk report.
3. **Step 3**: Open **Power BI Desktop**, open your RetainIQ report file, and click **Refresh** on the Home ribbon. All KPI cards, charts, and the Daily Action Queue table will immediately update with the fresh predictions.

---

## 🗣️ How to Explain Phase 4 in Interviews or Project Reviews

> *"In Phase 4, we completed end-to-end integration testing and validation. We verified the complete data lifecycle: raw transactional records are ingested into SQL, transformed into behavioral RFM features, scored by the Scikit-Learn Random Forest model, and segmented into risk tiers. The system automatically triggers daily HTML email alerts via Gmail OAuth for accounts exceeding 80% risk, while the Power BI Control Tower provides executive visibility."*
