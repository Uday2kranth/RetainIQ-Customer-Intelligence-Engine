# 📊 Stage 6: Power BI Executive Control Tower (RetainIQ Dashboard)

> **Voice Mode Explainer:**
> This document provides the complete, end-to-end conceptual and technical defense for the Power BI Executive Control Tower in the RetainIQ project. Use this for oral rehearsal with Gemini Voice on your phone.

---

## 1. The Dashboard Philosophy: "Single-Pane-of-Glass"

Modern business executives and customer success leads do not have time to click through 10 confusing dashboard tabs or slice through raw pivot tables. 

RetainIQ's Power BI Dashboard (`powerbi/RetainIQ_Control_Tower.pbix`) is engineered as a **1-Page "Single-Pane-of-Glass" Control Tower**. It implements a strict top-to-bottom visual hierarchy designed around **cognitive ergonomics**:
1. **Row 1 (Top):** *Macro Health* — "How is our business doing right now?"
2. **Row 2 (Middle):** *Diagnostic Root Causes* — "Why and where are customers leaving?"
3. **Row 3 (Bottom):** *Tactical Execution* — "What exact action should our account reps take today?"

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ TIER 1: EXECUTIVE SCORECARDS (Row 1)                                        │
│ Total Customers: 5,630 │ Retention: 86.31% │ Churn: 13.69% │ High-Risk: 339 │
├──────────────────────────────────────┬──────────────────────────────────────┤
│ TIER 2A: ROOT CAUSE 1 (Row 2 Left)   │ TIER 2B: ROOT CAUSE 2 (Row 2 Right)  │
│ Churn Rate by Category (Bar Chart)   │ Churn Risk by Tenure 0-70 Mos (Line) │
│ [Grocery leads at 16.0%]             │ [New Customer Cliff: 0-6 months]     │
├──────────────────────────────────────┴──────────────────────────────────────┤
│ TIER 3: TACTICAL OPERATIONAL QUEUE (Row 3 - Full Width Table)               │
│ Customer ID │ Churn Risk % │ Risk Tier │ Active Complaint? │ Action Prescribed│
│ 54313       │ 97.57%       │ High      │ Yes (Ticket Open) │ Urgent Outreach  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Visual Component Deep-Dive

### Row 1: The Executive Scorecard (4 KPI Cards)
* **Card 1: Total Customer Base (`5,630`)**
  * Sourced from `v_executive_kpis[total_customers]`.
  * Unit display set to `None` to show exact head count rather than `5.63K`.
* **Card 2: Customer Retention Rate (`86.31%`)**
  * Sourced from `v_executive_kpis[retention_rate_pct]`.
  * Formatted to 2 decimal places in vibrant Forest Green (`#16A34A`).
* **Card 3: Historical Churn Rate (`13.69%`)**
  * Sourced from `v_executive_kpis[churn_rate_pct]`.
  * Formatted to 2 decimal places.
* **Card 4: High-Risk Intervention Accounts (`339`)**
  * Sourced from `v_executive_kpis[high_risk_customers]`.
  * Formatted in bold Warning Red (`#DC2626`). Represents the exact count of accounts flagged by the Random Forest model with $\ge 80\%$ churn probability.

### Row 2: Diagnostic Root Causes (2 Analytical Charts)
* **Left Visual: Churn Rate by Product Category (Clustered Column Chart)**
  * *X-Axis:* `prefered_order_cat` | *Y-Axis:* `avg_churn_rate_pct`.
  * *Key Story:* **Grocery** has the highest churn rate at **16.0%**, followed by **Laptop & Accessories (13.9%)**, **Others (13.8%)**, **Fashion (13.5%)**, and **Mobile Phone (11.4%)**.
  * *Business Insight:* Grocery customers suffer from supply freshness or delivery fulfillment issues, requiring targeted operational review.
* **Right Visual: Churn Risk by Customer Tenure (Continuous Line Chart)**
  * *X-Axis:* `tenure` (0 to 70 months) | *Y-Axis:* `avg_churn_risk_pct`.
  * *Key Story:* Uncovers the **"New Customer Cliff"**. Churn risk peaks at **40%+** during the first 6 months of customer life. After month 15, the curve flattens to a stable ~15%.
  * *Business Insight:* Onboarding friction in the first 90 days is our primary revenue leak; long-tenured customers are highly sticky.

### Row 3: Daily High-Priority Action Queue (Full-Width Operational Table)
* **Visual:** Table visual pre-filtered from `v_daily_action_queue.csv`.
* **Columns:** `Customer ID`, `Churn Risk %`, `Risk Tier`, `Active Complaint?`, `Tenure (Months)`, `RFM Segment`, `Recommended Action`.
* **Configuration:** All numeric aggregations set to **"Don't summarize"** so each at-risk customer is rendered as an individual, actionable entity.
* **Sort Order:** Sorted descending by `Churn Risk %` (Customer `54313` at `97.57%` risk is #1 on the list).
* **Intervention Logic:** Tells account managers whether to dispatch an urgent support escalation, loyalty credit, or VIP re-engagement package.

---

## 3. Top 5 Power BI Defense Questions & Winning Answers

### Q1: Why Power BI instead of Python charts (Matplotlib/Seaborn) or a web app (Streamlit)?
> **Winning Answer:**  
> *"Matplotlib and Seaborn produce static, non-interactive images suitable for research papers, not executive decision-making. Streamlit requires coding and hosting maintenance for every layout tweak.*  
> *Power BI is the enterprise standard for business intelligence. It provides:*  
> *1. **Interactive Cross-Filtering:** Clicking on the 'Grocery' bar instantly filters the bottom action table to show only high-risk grocery customers.*  
> *2. **Self-Service Analytics:** Business stakeholders can sort, drill through, and export data without needing a data scientist.*  
> *3. **Enterprise Governance:** Scheduled refreshes, role-based access control, and seamless Microsoft ecosystem integration."*

---

### Q2: How does data flow from your SQL database and Machine Learning model into Power BI?
> **Winning Answer (The Architectural Bridge):**  
> *"We designed a zero-latency decoupled bridge between our backend and Power BI:*  
> *1. In Phase 1–3, our pipeline ingests customer data, computes RFM scores, and runs Random Forest predictions in SQL.*  
> *2. We defined analytical SQL views (`v_executive_kpis`, `v_daily_action_queue`, `v_churn_drivers`) directly inside `src/db/schema.py` to pre-aggregate metrics.*  
> *3. In Phase 5 of `run_pipeline.py`, an automated exporter dumps these views as optimized CSVs into `data/processed/`.*  
> *4. Power BI Desktop points directly to these local CSV views, allowing instant 1-click refreshes with zero query latency."*

---

### Q3: Why did you compute aggregations inside SQL Views instead of Power Query (M) or DAX?
> **Winning Answer (Database Pushdown Optimization):**  
> *"In production data architectures, the golden rule is **'Transform as far upstream as possible, and as far downstream as necessary.'**  
> *By pushing complex window functions, joins, and case statements into SQL views (`v_churn_drivers`, `v_daily_action_queue`), the database engine leverages indexing and optimized query plans.*  
> *This keeps the Power BI data model lightweight and fast, reserving DAX strictly for dynamic visual-level aggregations and KPI calculations."*

---

### Q4: What key business findings did your dashboard reveal?
> **Winning Answer:**  
> *"The Control Tower uncovered two critical business patterns that acquisition teams missed:*  
> *1. **The 'New Customer Cliff':** Customers in months 0 to 6 experience a 40%+ churn risk, indicating that onboarding friction and first-order delivery delays are driving attrition.*  
> *2. **The Complaint Multiplier:** In our daily action queue, 100% of the top 10 highest-risk customers have open customer complaints (`Active Complaint = Yes`). Resolving tickets within 24 hours is our highest-ROI retention lever."*

---

### Q5: How does the live dynamic refresh demonstration work during your presentation?
> **Winning Answer:**  
> *"We designed a powerful live demonstration sequence:  
> 1. We show the Control Tower sitting at our clean historical baseline: 5,630 customers and 339 high-risk accounts.  
> 2. In the terminal, we execute `python run_pipeline.py --simulate`, which simulates today's incoming batch of 35 new customer transactions with early-tenure complaint friction.  
> 3. Within 3 seconds, the database updates, RFM recalculates, ML scores the batch, and analytical CSVs are re-exported.  
> 4. We switch to Power BI Desktop and click **Home > Refresh** right in front of the mentors: Power BI's VertiPaq memory engine repaints the canvas, and they watch the Total Customers card visibly live-tick from **5,630 to 5,665**!  
> 5. We also have an instant `--reset` command to restore the pristine baseline anytime."*

---

## 4. Visual Build Guide Reference
* The complete step-by-step build manual with all 5 development screenshots is available in:  
  `study_pack/06_POWER_BI_CONTROL_TOWER/POWERBI_STEP_BY_STEP_BUILD_GUIDE.md`
* Includes exact UI navigation paths for modern Power BI Desktop (Visual tab, Callout grouping, color hex codes, and axis formatting).

---

## 5. Verbatim 45-Second Mentor Pitch (Memorize This!)

> *"For business consumption, we designed the Power BI Control Tower following a strict 1-page 'Single-Pane-of-Glass' architecture to prevent cognitive overload.*
> 
> *Row 1 acts as our executive scoreboard, displaying our 5,630 customer base, an 86.3% retention rate, and a flagged cohort of 339 high-risk accounts.*
> 
> *Row 2 diagnoses the root causes: it highlights Grocery as our highest-churn department at 16.0%, and our 70-month tenure curve proves that churn risk spikes heavily within the first 6 months before stabilizing.*
> 
> *Finally, Row 3 transforms this intelligence into tactical execution: it gives customer success teams an unsummarized daily action queue sorted by risk, with prescribed AI intervention offers like support escalation and retention credits."*
