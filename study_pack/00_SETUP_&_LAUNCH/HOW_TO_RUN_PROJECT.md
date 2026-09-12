# 🚀 How to Setup & Run the RetainIQ Project

> **Phone / Voice Mode Summary:**
> This guide walks through the exact steps to launch the project from zero — activating the virtual environment, verifying configurations, running the automated tests, and executing the full pipeline in all 3 operational modes.

---

## 1. Virtual Environment Activation

The project uses a Python virtual environment located in `.venv/`.

### In PowerShell (Windows):
```powershell
.venv\Scripts\Activate.ps1
```
* **How to know it worked:** Your terminal prompt will display `(.venv)` at the beginning of the line.
* **If PowerShell blocks scripts:** Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and try again.

---

## 2. Dependencies & Libraries

All required libraries are listed in `requirements.txt`.
To install or verify:
```powershell
pip install -r requirements.txt
```
### Key Packages Used:
* **Data & Math:** `pandas`, `numpy`, `scipy`
* **Database:** `sqlalchemy`
* **Machine Learning:** `scikit-learn`, `joblib`
* **Workflow Orchestration:** `apache-airflow` (Linux/Docker cluster; gracefully skipped on Windows via PEP 508 marker `sys_platform != 'win32'`)
* **Google API:** `google-api-python-client`, `google-auth-oauthlib`, `google-auth-httplib2`
* **Testing:** `pytest`

---

## 3. Configuration & Secrets (`src/config.py`)

All system settings are consolidated in `src/config.py`:
* **Database URI:** Defaults to SQLite (`data/retainiq_local.db`).
* **Risk Threshold:** `HIGH_RISK_THRESHOLD = 0.80` (Churn risk $\ge 80\%$ triggers alerts).
* **Alert Recipients:** 
  `DEFAULT_MANAGER_EMAIL = "p.udaykranthg1dataanalytics@gmail.com, udaykranth01@gmail.com, udaykranthi4@gmail.com"`
* **OAuth Credentials:** `credentials.json` and `token.json` stored in the project root.

---

## 4. How to Run the Project (The 3 Operational Runner Modes)

Our master runner (`run_pipeline.py`) provides 3 operational execution modes tailored for live demonstration and defense:

### Mode 1: Standard Baseline Run (2.3 Seconds)
```powershell
python run_pipeline.py
```
* **Execution:** Ingests 5,630 Kaggle customer records, calculates RFM loyalty quintiles, generates Random Forest probabilities, emails the alert, and exports 6 CSV datasets.
* **Result:** Database contains **5,630 customers** and flags **339 high-risk accounts**.

### Mode 2: Live Dynamic Batch Simulation (For the Demo!)
```powershell
python run_pipeline.py --simulate
```
* **Execution:** Simulates today's incoming operational batch of **35 new customer orders & complaints**. Appends them to SQL, recalculates RFM, scores ML predictions, sends a fresh email alert, and exports updated CSVs.
* **Result:** Total volume becomes **5,665 customers**.
* **The Magic Moment:** In Power BI, click **Home > Refresh** $\rightarrow$ watch the Total Customers card live-tick from **5,630 to 5,665**!

### Mode 3: Instant Reset Switch (Back to Baseline)
```powershell
python run_pipeline.py --reset
```
* **Execution:** Deletes the simulated batch and restores the database back to the pristine 5,630 baseline in 2.4 seconds.

---

## 5. Automated Testing Suite

To verify system health and ensure all 5 layers work without regressions:
```powershell
python -m pytest tests/test_pipeline_e2e.py -v
```
* **Expected Output:** `7 passed in ~4.10s`.
* Validates database creation, ingestion, RFM scores, ML inference, alerting, SQL views, and Power BI CSV exports.

---

## 6. Power BI Control Tower Connection

1. Open `powerbi/RetainIQ_Control_Tower.pbix` in Power BI Desktop.
2. Clicking **Home > Refresh** in the top ribbon reloads the processed CSV files from `data/processed/` in under 2 seconds.
