-- ============================================================================
-- RetainIQ: Optimized SQL Views for Power BI Control Tower & Dashboards
-- Compatible with PostgreSQL, MySQL, and SQLite
-- ============================================================================

-- 1. Executive Summary KPIs View (For Card Visuals & Top-Level Metrics)
CREATE VIEW IF NOT EXISTS v_executive_kpis AS
SELECT
    COUNT(r.customer_id) AS total_customers,
    SUM(r.churn) AS historical_churned_customers,
    ROUND(AVG(r.churn) * 100.0, 2) AS historical_churn_rate_pct,
    ROUND((1.0 - AVG(r.churn)) * 100.0, 2) AS retention_rate_pct,
    ROUND(AVG(p.churn_risk_pct), 2) AS average_portfolio_risk_pct,
    SUM(CASE WHEN p.churn_probability >= 0.80 THEN 1 ELSE 0 END) AS high_risk_customers_count,
    SUM(CASE WHEN p.churn_probability >= 0.50 AND p.churn_probability < 0.80 THEN 1 ELSE 0 END) AS medium_risk_customers_count,
    SUM(CASE WHEN p.churn_probability < 0.50 THEN 1 ELSE 0 END) AS low_risk_customers_count,
    ROUND(AVG(r.satisfaction_score), 2) AS avg_satisfaction_score,
    ROUND(AVG(r.cashback_amount), 2) AS avg_cashback_amount
FROM raw_customers r
LEFT JOIN churn_predictions p ON r.customer_id = p.customer_id;


-- 2. Daily Action Queue View (For Support & Sales Managers Table Visual)
CREATE VIEW IF NOT EXISTS v_daily_action_queue AS
SELECT
    r.customer_id,
    p.churn_risk_pct,
    p.risk_tier,
    r.tenure AS tenure_months,
    r.satisfaction_score,
    CASE WHEN r.complain = 1 THEN 'Yes (Active Ticket)' ELSE 'No' END AS complaint_status,
    r.prefered_order_cat,
    r.preferred_payment_mode,
    r.day_since_last_order,
    r.order_count,
    r.cashback_amount,
    f.rfm_segment,
    f.r_score,
    f.f_score,
    f.m_score,
    CASE 
        WHEN p.churn_probability >= 0.80 AND r.complain = 1 THEN 'URGENT: Support Escalation & Retention Credit'
        WHEN p.churn_probability >= 0.80 AND r.tenure <= 6 THEN 'Onboarding Outreach & Personal Discount'
        WHEN p.churn_probability >= 0.80 THEN 'Targeted Win-Back Campaign'
        WHEN p.churn_probability >= 0.50 THEN 'Engagement Email & Product Recommendation'
        ELSE 'Standard Loyalty Nurture'
    END AS recommended_action
FROM raw_customers r
INNER JOIN churn_predictions p ON r.customer_id = p.customer_id
LEFT JOIN rfm_features f ON r.customer_id = f.customer_id
ORDER BY p.churn_probability DESC;


-- 3. Churn Drivers & Behavioral Diagnostics View
CREATE VIEW IF NOT EXISTS v_churn_drivers AS
SELECT
    r.prefered_order_cat,
    r.city_tier,
    r.preferred_payment_mode,
    COUNT(r.customer_id) AS customer_count,
    SUM(r.churn) AS churn_count,
    ROUND(AVG(r.churn) * 100.0, 2) AS category_churn_rate_pct,
    ROUND(AVG(p.churn_risk_pct), 2) AS predicted_avg_risk_pct,
    ROUND(AVG(r.tenure), 1) AS avg_tenure,
    ROUND(AVG(r.complain) * 100.0, 1) AS complaint_rate_pct,
    ROUND(AVG(r.satisfaction_score), 2) AS avg_satisfaction
FROM raw_customers r
LEFT JOIN churn_predictions p ON r.customer_id = p.customer_id
GROUP BY r.prefered_order_cat, r.city_tier, r.preferred_payment_mode;


-- 4. RFM Segmentation Performance View
CREATE VIEW IF NOT EXISTS v_rfm_matrix AS
SELECT
    f.rfm_segment,
    COUNT(f.customer_id) AS segment_size,
    ROUND(AVG(p.churn_risk_pct), 2) AS avg_churn_risk_pct,
    SUM(CASE WHEN p.churn_probability >= 0.80 THEN 1 ELSE 0 END) AS high_risk_count,
    ROUND(AVG(f.recency_days), 1) AS avg_recency_days,
    ROUND(AVG(f.frequency_orders), 1) AS avg_order_count,
    ROUND(AVG(f.monetary_cashback), 2) AS avg_cashback
FROM rfm_features f
LEFT JOIN churn_predictions p ON f.customer_id = p.customer_id
GROUP BY f.rfm_segment;
