# 🚨 Stage 4: Automated Gmail OAuth 2.0 Alerts

> **Voice Mode Explainer:**
> This stage turns predictive insight into immediate operational action: querying high-risk accounts (>80% risk), building a responsive HTML briefing, and dispatching live email notifications via Google's secure OAuth 2.0 API.

---

## 1. What Happens at This Stage?
1. **Queries High-Risk Accounts:** Filters SQLite for all accounts where `churn_probability >= 0.80` (identifying 339 accounts).
2. **Builds HTML Email Briefing:** Generates a formatted executive summary:
   * **Headline Banner:** `339 High-Risk Customers Identified | Threshold: Risk ≥ 80%`.
   * **Tactical Table:** Top 15 highest-priority customer intervention rows, complete with customer ID, churn risk %, tenure, complaint flag (`Yes ⚠️`), RFM segment, and recommended retention offer.
3. **Authenticates via OAuth 2.0:** Loads `token.json` (or uses `credentials.json` for first-time consent).
4. **Dispatches Live Email:** Sends the message via Google's Gmail API servers (`service.users().messages().send()`).
5. **Multi-Recipient Broadcast:** Dispatches simultaneously to:
   * Retention Manager: `p.udaykranthg1dataanalytics@gmail.com`
   * Support Team: `udaykranth01@gmail.com`, `udaykranthi4@gmail.com`
6. **Audit Trail:** Writes the dispatch record into SQL table `alert_history` for compliance and auditability.

---

## 2. Key Engineering Decisions & Why We Made Them

### Why Gmail OAuth 2.0 Instead of Plain SMTP Passwords?
* **Zero Hardcoded Secrets:** Hardcoding email passwords in source code violates modern security standards and risks credential leaks in GitHub.
* **Token-Based Auth:** OAuth 2.0 uses secure, revocable tokens. The application only requests the narrowest required permission (`https://www.googleapis.com/auth/gmail.send`).
* **Why Tokens Don't Expire:** In Google Cloud Console, our OAuth app is published to **"In Production"** with an unverified 100-user developer cap. Refresh tokens remain permanently active without expiring in 7 days!

### Why Combine the Summary and Action Queue in One Email?
* **Executive + Operational Alignment:** Having the high-level KPI count on top allows the manager to immediately see portfolio risk, while the detailed table below gives frontline reps their daily call list. Both personas stay synchronized on the exact same data.

---

## 3. What to Say to Your Mentor (30 Seconds)

> *"Stage 4 bridges machine learning with daily business execution.*
> 
> *Our alerting module queries accounts exceeding our 80% churn risk threshold and generates an automated HTML priority queue. Using enterprise Gmail OAuth 2.0 token authentication rather than insecure plaintext passwords, it dispatches the live notification to both the Retention Manager and frontline support leads.*
> 
> *Every dispatch event is logged into our SQL `alert_history` audit table, creating a complete historical audit trail of our retention interventions."*
