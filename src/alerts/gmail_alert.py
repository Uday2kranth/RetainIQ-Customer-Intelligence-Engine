import os
import base64
import logging
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
from src.config import (
    CREDENTIALS_PATH, TOKEN_PATH, GMAIL_SCOPES, DEFAULT_MANAGER_EMAIL,
    HIGH_RISK_THRESHOLD, DATA_DIR
)
from src.db.connection import get_engine
from src.db.schema import AlertHistory

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def get_gmail_service():
    """
    Authenticates and constructs the Google Gmail API service using OAuth 2.0.
    Checks for token.json first, falls back to credentials.json for interactive consent.
    """
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), GMAIL_SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif os.path.exists(CREDENTIALS_PATH):
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), GMAIL_SCOPES)
            creds = flow.run_local_server(port=0)
            with open(TOKEN_PATH, "w") as token_file:
                token_file.write(creds.to_json())
        else:
            return None
            
    return build("gmail", "v1", credentials=creds)

def build_alert_html(high_risk_df: pd.DataFrame) -> str:
    """Constructs a responsive, formatted HTML email report for the Sales Manager."""
    total_flagged = len(high_risk_df)
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Build customer rows (top 15 for summary email)
    rows_html = ""
    for _, row in high_risk_df.head(15).iterrows():
        cid = row.get("customer_id", "N/A")
        risk = row.get("churn_risk_pct", 0)
        tenure = int(row.get("tenure", 0)) if pd.notnull(row.get("tenure")) else 0
        complain = "Yes ⚠️" if row.get("complain", 0) == 1 else "No"
        segment = row.get("rfm_segment", "At Risk")
        sat = row.get("satisfaction_score", "N/A")

        rows_html += f"""
        <tr style="border-bottom: 1px solid #e2e8f0; font-size: 13px;">
            <td style="padding: 10px; font-weight: bold; color: #1e293b;">#{cid}</td>
            <td style="padding: 10px; color: #dc2626; font-weight: bold;">{risk}%</td>
            <td style="padding: 10px; color: #475569;">{tenure} mos</td>
            <td style="padding: 10px; color: #b91c1c;">{complain}</td>
            <td style="padding: 10px; color: #334155;">{sat} / 5</td>
            <td style="padding: 10px; color: #2563eb; font-weight: 500;">{segment}</td>
            <td style="padding: 10px; color: #059669; font-weight: 600;">Reach Out & Offer Retention Credit</td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
    </head>
    <body style="font-family: Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 24px;">
        <div style="max-width: 800px; margin: 0 auto; background: #ffffff; border-radius: 8px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
            
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 24px; color: #ffffff;">
                <h2 style="margin: 0 0 8px 0; font-size: 22px; color: #38bdf8;">🚨 RetainIQ: Daily Churn Prevention Alert</h2>
                <p style="margin: 0; font-size: 14px; color: #94a3b8;">High-Risk Customer Queue for E-Commerce Sales & Support Teams | {now_str}</p>
            </div>

            <!-- Executive Summary -->
            <div style="padding: 24px; border-bottom: 1px solid #e2e8f0;">
                <p style="font-size: 15px; color: #334155; line-height: 1.5; margin: 0 0 16px 0;">
                    Hello Sales & Support Team,<br><br>
                    The <strong>RetainIQ Automated Pipeline</strong> has identified 
                    <strong style="color: #dc2626; font-size: 16px;">{total_flagged} accounts</strong> with a predicted churn probability 
                    exceeding the <strong>80% threshold</strong>. Please review the high-priority queue below and initiate retention outreach today.
                </p>
                
                <div style="display: flex; gap: 12px; margin-top: 12px;">
                    <div style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 6px; padding: 12px 20px;">
                        <span style="font-size: 12px; color: #991b1b; font-weight: bold; text-transform: uppercase;">High Risk Flagged</span>
                        <div style="font-size: 24px; font-weight: bold; color: #dc2626;">{total_flagged}</div>
                    </div>
                </div>
            </div>

            <!-- Action Queue Table -->
            <div style="padding: 24px;">
                <h3 style="margin: 0 0 16px 0; font-size: 16px; color: #0f172a;">Daily High-Risk Priority Queue (Top Accounts)</h3>
                <table style="width: 100%; border-collapse: collapse; text-align: left;">
                    <thead>
                        <tr style="background: #f1f5f9; color: #475569; font-size: 12px; text-transform: uppercase;">
                            <th style="padding: 10px;">Customer ID</th>
                            <th style="padding: 10px;">Churn Risk</th>
                            <th style="padding: 10px;">Tenure</th>
                            <th style="padding: 10px;">Complaint</th>
                            <th style="padding: 10px;">Satisfaction</th>
                            <th style="padding: 10px;">RFM Segment</th>
                            <th style="padding: 10px;">Recommended Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
            </div>

            <!-- Footer -->
            <div style="background: #f8fafc; padding: 16px 24px; border-top: 1px solid #e2e8f0; font-size: 12px; color: #64748b;">
                <p style="margin: 0;">Automated notification generated by RetainIQ Intelligence Engine (Airflow Task 4). View full interactive analytics on Power BI Control Tower.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html

def send_churn_alerts(engine=None, recipient_email: str = None) -> dict:
    """
    Task 4 (Email Action):
    Queries customers with >80% churn risk from SQL, constructs an HTML email report,
    and dispatches the notification via Gmail OAuth 2.0 API (or generates simulated offline report if credentials pending).
    """
    eng = engine or get_engine()
    recipient = recipient_email or DEFAULT_MANAGER_EMAIL

    logger.info("Querying SQL for high-risk customers (>80% risk)...")
    query = """
    SELECT 
        p.customer_id,
        p.churn_risk_pct,
        p.risk_tier,
        r.tenure,
        r.satisfaction_score,
        r.complain,
        r.cashback_amount,
        f.rfm_segment
    FROM churn_predictions p
    LEFT JOIN raw_customers r ON p.customer_id = r.customer_id
    LEFT JOIN rfm_features f ON p.customer_id = f.customer_id
    WHERE p.churn_probability >= :threshold
    ORDER BY p.churn_probability DESC
    """
    try:
        high_risk_df = pd.read_sql(query, con=eng, params={"threshold": HIGH_RISK_THRESHOLD})
    except Exception as e:
        logger.warning(f"Error querying joined tables with params ({e}). Falling back to simple query.")
        high_risk_df = pd.read_sql(
            f"SELECT * FROM churn_predictions WHERE churn_probability >= {HIGH_RISK_THRESHOLD} ORDER BY churn_probability DESC",
            con=eng
        )

    total_high_risk = len(high_risk_df)
    logger.info(f"Found {total_high_risk} customers exceeding {HIGH_RISK_THRESHOLD*100}% churn risk.")

    html_content = build_alert_html(high_risk_df)
    
    # Always save latest HTML alert report for local viewing/Power BI linking
    alert_html_path = DATA_DIR / "latest_alert_email.html"
    with open(alert_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    logger.info(f"Saved latest alert report preview to {alert_html_path}")

    # Attempt Gmail OAuth API sending
    service = None
    status = "MOCKED"
    details = f"Local preview saved to {alert_html_path} ({total_high_risk} high-risk customers)."

    try:
        service = get_gmail_service()
        if service:
            message = MIMEMultipart("alternative")
            message["Subject"] = f"🚨 RetainIQ Alert: {total_high_risk} High-Risk Customers Identified"
            message["From"] = "me"
            message["To"] = recipient
            message.attach(MIMEText(html_content, "html"))

            raw_msg = base64.urlsafe_b64encode(message.as_bytes()).decode()
            sent_msg = service.users().messages().send(userId="me", body={"raw": raw_msg}).execute()
            status = "SENT"
            details = f"Email dispatched via Gmail API (Message ID: {sent_msg.get('id')}) to {recipient}."
            logger.info(f"Successfully sent Gmail alert: {details}")
        else:
            logger.info("Gmail OAuth credentials pending. Generated full local HTML preview and logged alert.")
    except Exception as e:
        status = "FAILED"
        details = f"Gmail API error: {str(e)}"
        logger.warning(f"Could not send email via Gmail API: {e}")

    # Record in SQL alert_history table
    try:
        history_record = pd.DataFrame([{
            "batch_timestamp": datetime.now(timezone.utc),
            "total_high_risk_flagged": total_high_risk,
            "recipient_email": recipient,
            "status": status,
            "details": details
        }])
        history_record.to_sql("alert_history", con=eng, if_exists="append", index=False)
        logger.info("Recorded alert event in alert_history table.")
    except Exception as e:
        logger.warning(f"Could not write to alert_history ({e})")

    return {
        "status": status,
        "total_high_risk_flagged": total_high_risk,
        "recipient_email": recipient,
        "details": details,
        "html_preview_path": str(alert_html_path),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

if __name__ == "__main__":
    send_churn_alerts()
