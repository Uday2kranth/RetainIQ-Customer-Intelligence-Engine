import datetime
from pathlib import Path
from sqlalchemy import (
    Column, Integer, Float, String, DateTime, Boolean, Text, Index, text
)
from src.db.connection import Base, get_engine

class RawCustomer(Base):
    __tablename__ = "raw_customers"

    customer_id = Column(Integer, primary_key=True, index=True)
    tenure = Column(Float, nullable=True)
    preferred_login_device = Column(String(50), nullable=True)
    city_tier = Column(Integer, nullable=True)
    warehouse_to_home = Column(Float, nullable=True)
    preferred_payment_mode = Column(String(50), nullable=True)
    gender = Column(String(20), nullable=True)
    hour_spend_on_app = Column(Float, nullable=True)
    number_of_device_registered = Column(Integer, nullable=True)
    prefered_order_cat = Column(String(100), nullable=True)
    satisfaction_score = Column(Integer, nullable=True)
    marital_status = Column(String(50), nullable=True)
    number_of_address = Column(Integer, nullable=True)
    complain = Column(Integer, default=0)
    order_amount_hike_from_last_year = Column(Float, nullable=True)
    coupon_used = Column(Float, nullable=True)
    order_count = Column(Float, nullable=True)
    day_since_last_order = Column(Float, nullable=True)
    cashback_amount = Column(Float, nullable=True)
    churn = Column(Integer, default=0)
    ingested_at = Column(DateTime, default=datetime.datetime.utcnow)

class RFMFeature(Base):
    __tablename__ = "rfm_features"

    customer_id = Column(Integer, primary_key=True, index=True)
    recency_days = Column(Float, nullable=False)
    frequency_orders = Column(Float, nullable=False)
    monetary_cashback = Column(Float, nullable=False)
    r_score = Column(Integer, nullable=False)
    f_score = Column(Integer, nullable=False)
    m_score = Column(Integer, nullable=False)
    rfm_segment = Column(String(50), nullable=False)
    calculated_at = Column(DateTime, default=datetime.datetime.utcnow)

class ChurnPrediction(Base):
    __tablename__ = "churn_predictions"

    prediction_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, index=True, nullable=False)
    churn_probability = Column(Float, nullable=False)
    churn_risk_pct = Column(Float, nullable=False)
    risk_tier = Column(String(20), nullable=False)  # High (>=80%), Medium (50-79%), Low (<50%)
    predicted_churn = Column(Integer, nullable=False)
    predicted_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)

class AlertHistory(Base):
    __tablename__ = "alert_history"

    alert_id = Column(Integer, primary_key=True, autoincrement=True)
    batch_timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    total_high_risk_flagged = Column(Integer, nullable=False)
    recipient_email = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False)  # SENT, MOCKED, FAILED
    details = Column(Text, nullable=True)

def init_db(engine=None):
    """
    Initializes all database tables and analytical views.
    Guarantees that tables and views exist for Power BI without manual steps.
    """
    eng = engine or get_engine()
    Base.metadata.create_all(bind=eng)

    # Automatically execute analytical views DDL
    views_path = Path(__file__).resolve().parent.parent / "powerbi" / "powerbi_views.sql"
    if views_path.exists():
        with open(views_path, "r", encoding="utf-8") as f:
            sql_script = f.read()
        with eng.connect() as conn:
            for stmt in sql_script.split(";"):
                stmt = stmt.strip()
                if stmt:
                    conn.execute(text(stmt))
            conn.commit()
    return eng

