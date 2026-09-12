# 🗄️ Stage 1: SQL Database & Ingestion

> **Voice Mode Explainer:**
> This stage handles the data foundation: connecting to SQLite, building analytical views, ingesting 5,630 baseline customer accounts, and providing live batch simulation for dynamic Power BI refresh.

---

## 1. What Happens at This Stage?
1. **Connects to Database:** Connects to our local SQLite database at `data/retainiq_local.db` via SQLAlchemy.
2. **Initializes Schema:** Creates core tables (`raw_customers`, `rfm_features`, `churn_predictions`, `alert_history`).
3. **Auto-Compiles SQL Views:** Automatically reads and runs `powerbi/powerbi_views.sql` to build the 4 analytical views for Power BI.
4. **Baseline Ingestion:** Ingests 5,630 Kaggle customer accounts into `raw_customers` (`mode='baseline'`).
5. **Live Batch Simulation:** Provides `simulate_incoming_batch()` to append 35 new realistic accounts with early-tenure complaints for dynamic demonstration (`python run_pipeline.py --simulate`).
6. **Instant Reset Switch:** Provides `--reset` to restore the pristine 5,630 baseline in 2.4 seconds.

---

## 2. Key Engineering Decisions & Why We Made Them

### Why SQLite Instead of PostgreSQL for This Deployment?
* **Zero Configuration:** Runs 100% natively on Windows without requiring Docker, background Windows services, or password authentication issues.
* **Full ACID Compliance:** Guarantees transactional data integrity and supports standard SQL syntax, foreign keys, and analytical views.
* **Seamless Scalability:** The SQLAlchemy engine abstraction in `src/db/connection.py` allows switching to enterprise PostgreSQL simply by changing one environment variable (`RETAINIQ_DB_ENGINE=postgres`).

### How Does the Incremental Batch Simulation Work?
* Reads `SELECT MAX(customer_id) FROM raw_customers` (starts at `55630`).
* Generates 35 incremental accounts (`55631` to `55665`).
* Seeds ~35% with active customer complaints and low tenure (0–3 months) to simulate real-world customer friction.
* Appends them to SQL using `if_exists="append"`.
* When Power BI is refreshed, the mentor watches the cards live-tick from **5,630 to 5,665**!

---

## 3. What to Say to Your Mentor (30 Seconds)

> *"In Stage 1, our ingestion module in `src/etl/ingest.py` connects to our SQL database via SQLAlchemy and manages our customer data foundation.*
> 
> *We implemented a dual-mode ingestion architecture: a standard baseline of 5,630 Kaggle records, alongside an incremental batch simulator that appends incoming daily orders and complaint tickets on demand.*
> 
> *This allows us to demonstrate live, real-time pipeline telemetry in Power BI—watching the cards live-tick from 5,630 to 5,665—while maintaining a deterministic reset switch to restore our baseline in under 3 seconds."*
