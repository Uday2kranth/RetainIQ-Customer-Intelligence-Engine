# 📊 Phase 2 User Playbook: Power BI Control Tower & Action Queue

This guide is designed for **you (the user)**. It provides exact, step-by-step instructions for importing the project data into **Power BI Desktop**, applying the DAX measures, and creating the **Executive Dashboard** and **Daily Action Queue** visual layouts matching your approved presentation slides.

---

## 🧭 Overview: What AI Built vs. What You Will Do

```
┌──────────────────────────────────────────────┐
│  AI Built:                                   │
│  - Pre-aggregated SQL Views (powerbi_views)  │
│  - Complete Catalog of DAX Measures (.dax)   │
│  - Data Model Relationships Schema           │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│  You Will Do (In Power BI Desktop):          │
│  1. Connect to Local Database / Import Tables│
│  2. Verify Relationships in Model View       │
│  3. Copy & Paste the DAX Measures            │
│  4. Drag & Drop Visuals onto the Canvas      │
└──────────────────────────────────────────────┘
```

---

## 🚀 Step 1: Open Power BI Desktop & Load Project Data

Power BI Desktop is already installed on your PC.

### Option A: Import from Local Database File (Fastest & Simplest)
1. Open **Power BI Desktop**.
2. On the home ribbon, click **Get Data** ➔ **Text/CSV** (or **ODBC** / **SQLite/PostgreSQL**).
3. If importing via files, navigate to your project directory:
   - `d:\important_cmd_history\project fopr suretrust\data\raw\ecommerce_customer_churn.csv` (or use database connector).
4. Click **Load**.

### Option B: Connect to PostgreSQL (If using PostgreSQL service)
1. Click **Get Data** ➔ **PostgreSQL Database**.
2. **Server**: `localhost:5432`
3. **Database**: `retainiq_db`
4. Select the tables: `raw_customers`, `rfm_features`, `churn_predictions`, and views `v_executive_kpis`, `v_daily_action_queue`.
5. Click **Load**.

---

## 🔗 Step 2: Set Data Model Relationships (Model View)

1. Click the **Model view** icon on the left sidebar (the 3 connected boxes icon).
2. Ensure the following **1-to-1 / 1-to-Many** relationships are active:
   * `raw_customers[customer_id]` ➔ `churn_predictions[customer_id]` (1 to 1)
   * `raw_customers[customer_id]` ➔ `rfm_features[customer_id]` (1 to 1)

---

## 📐 Step 3: Add DAX Measures

In the **Report view** (top left icon):
1. In the **Data** pane on the right, right-click on the `churn_predictions` table.
2. Select **New Measure**.
3. Copy and paste each DAX formula from [`powerbi/dax_measures.dax`](file:///d:/important_cmd_history/project%20fopr%20suretrust/powerbi/dax_measures.dax):

```dax
// 1. Total Customers
Total Customers = COUNTROWS('raw_customers')

// 2. Churn Rate %
Historical Churn Rate % = 
DIVIDE(CALCULATE(COUNTROWS('raw_customers'), 'raw_customers'[churn] = 1), [Total Customers], 0) * 100

// 3. Retention Rate %
Retention Rate % = 100 - [Historical Churn Rate %]

// 4. High Risk Customers Count
High Risk Customers Count = 
CALCULATE(COUNTROWS('churn_predictions'), 'churn_predictions'[churn_risk_pct] >= 80)

// 5. Avg Portfolio Risk %
Avg Churn Risk % = AVERAGE('churn_predictions'[churn_risk_pct])
```

---

## 🎨 Step 4: Build the Visual Dashboard Canvas

### 📌 Row 1: Executive KPI Cards (Slide 1 Style)
Create 4 **Card Visuals** across the top:
* **Card 1**: `[Total Customers]` ➔ Label: **Total Customers** (~5,630)
* **Card 2**: `[Retention Rate %]` ➔ Label: **Customer Retention Rate** (Target: ~86.3%)
* **Card 3**: `[Historical Churn Rate %]` ➔ Label: **Churn Rate** (~13.7%)
* **Card 4**: `[High Risk Customers Count]` ➔ Label: **High-Risk Accounts (>80%)** (Callout color: Red `#DC2626`)

---

### 📌 Row 2: Behavioral Diagnostic Charts (Slide 1 & 2 Style)
1. **Donut / Bar Chart (Churn by Category)**:
   - **X-Axis / Legend**: `raw_customers[prefered_order_cat]`
   - **Values**: `[High Risk Customers Count]` or `[Avg Churn Risk %]`
   - *Insight*: Identifies which product lines (e.g. Mobile, Laptop) carry the greatest retention exposure.
2. **Column Chart (Churn Risk by Customer Tenure)**:
   - **X-Axis**: `raw_customers[tenure]`
   - **Y-Axis**: `[Avg Churn Risk %]`
   - *Insight*: Shows that new customer accounts (< 6 months) experience the highest churn probability.
3. **Clustered Bar Chart (RFM Segments Breakdown)**:
   - **Y-Axis**: `rfm_features[rfm_segment]`
   - **X-Axis**: `Count of customer_id`
   - *Insight*: Shows distribution between Champions, Loyal Customers, and At-Risk groups.

---

### 📌 Row 3: Daily Action Queue Table (Slide 4 Style)
Create a **Table Visual** at the bottom spanning full width:
* **Columns to Add**:
  1. `raw_customers[customer_id]`
  2. `churn_predictions[churn_risk_pct]` *(Format as 0.0%)*
  3. `churn_predictions[risk_tier]` *(High / Medium / Low)*
  4. `raw_customers[tenure]` *(Tenure in months)*
  5. `raw_customers[complain]` *(Flag: 1 for complaint)*
  6. `raw_customers[satisfaction_score]` *(Score 1-5)*
  7. `rfm_features[rfm_segment]`
* **Sort Order**: Sort descending by `churn_risk_pct`.
* **Conditional Formatting**: Add Red background/data bar for `churn_risk_pct >= 80%`.

---

## 🗣️ How to Explain Phase 2 in Interviews or Project Reviews

> *"For Phase 2, we built the RetainIQ Control Tower in Power BI Desktop. Rather than connecting raw, unoptimized data directly to visual cards, we designed pre-aggregated SQL analytical views and custom DAX measures. This allows executive sales managers to monitor real-time portfolio retention rates, while support teams get an interactive Daily Action Queue table pinpointing exact accounts with >80% churn risk and active complaints for immediate intervention."*
