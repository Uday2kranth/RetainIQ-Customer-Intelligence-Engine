"""
SKELETON CODE: Stage 4 - Automated Gmail OAuth 2.0 Alerts
File Reference: src/alerts/gmail_alert.py
"""
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from src.db.connection import get_engine
from src.config import TOKEN_PATH, DEFAULT_MANAGER_EMAIL

engine = get_engine()

# 1. Query high-risk customer records from SQL
query = "SELECT * FROM churn_predictions WHERE churn_probability >= 0.80 ORDER BY churn_probability DESC"
high_risk_df = pd.read_sql(query, con=engine)
total_flagged = len(high_risk_df)

# 2. Build HTML email report with top accounts
html_content = f"""
<h2>🚨 RetainIQ Alert: {total_flagged} High-Risk Customers Flagged</h2>
<p>Threshold: Churn Risk &ge; 80%. Immediate retention intervention required.</p>
<table border="1" cellpadding="8">
  <tr><th>Customer ID</th><th>Risk %</th><th>Tier</th></tr>
  {''.join(f'<tr><td>{row.customer_id}</td><td>{row.churn_risk_pct}%</td><td>{row.risk_tier}</td></tr>' for _, row in high_risk_df.head(10).iterrows())}
</table>
"""

# 3. Authenticate with Gmail OAuth 2.0
creds = Credentials.from_authorized_user_file(str(TOKEN_PATH))
service = build("gmail", "v1", credentials=creds)

# 4. Construct and dispatch message
message = MIMEMultipart("alternative")
message["Subject"] = f"🚨 RetainIQ Alert: {total_flagged} High-Risk Customers Identified"
message["From"] = "me"
message["To"] = DEFAULT_MANAGER_EMAIL # p.udaykranthg1dataanalytics@gmail.com, etc.
message.attach(MIMEText(html_content, "html"))

raw_bytes = base64.urlsafe_b64encode(message.as_bytes()).decode()
sent = service.users().messages().send(userId="me", body={"raw": raw_bytes}).execute()

print(f"✅ Email dispatched via Gmail API (Message ID: {sent['id']}) to {DEFAULT_MANAGER_EMAIL}")
