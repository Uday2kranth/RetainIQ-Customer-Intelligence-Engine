import os
from pathlib import Path

# Project Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Data Directories
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

RAW_DATA_PATH = RAW_DATA_DIR / "ecommerce_customer_churn.csv"
PROCESSED_DATA_PATH = PROCESSED_DATA_DIR / "rfm_features.parquet"
PROCESSED_CSV_PATH = PROCESSED_DATA_DIR / "rfm_features.csv"

# Models Directory
MODELS_DIR = BASE_DIR / "models"
MODEL_PATH = MODELS_DIR / "churn_model.pkl"
MODEL_METRICS_PATH = MODELS_DIR / "model_metrics.json"

# Credentials & OAuth
CREDENTIALS_PATH = BASE_DIR / "credentials.json"
TOKEN_PATH = BASE_DIR / "token.json"
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

# Business Logic & Risk Thresholds
HIGH_RISK_THRESHOLD = 0.80  # Churn probability >= 80% triggers alert
MEDIUM_RISK_THRESHOLD = 0.50
DEFAULT_MANAGER_EMAIL = os.getenv(
    "SALES_MANAGER_EMAIL",
    "p.udaykranthg1dataanalytics@gmail.com, udaykranth01@gmail.com, udaykranthi4@gmail.com"
)


# Database Configuration (PostgreSQL with SQLite fallback)
PG_USER = os.getenv("POSTGRES_USER", "postgres")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
PG_HOST = os.getenv("POSTGRES_HOST", "localhost")
PG_PORT = os.getenv("POSTGRES_PORT", "5432")
PG_DB = os.getenv("POSTGRES_DB", "retainiq_db")

# Primary connection string (PostgreSQL) and fallback (SQLite)
POSTGRES_DATABASE_URI = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"
SQLITE_DATABASE_URI = f"sqlite:///{DATA_DIR / 'retainiq_local.db'}"

# Active Database URI
DB_ENGINE_CHOICE = os.getenv("RETAINIQ_DB_ENGINE", "sqlite").lower()
DATABASE_URI = POSTGRES_DATABASE_URI if DB_ENGINE_CHOICE == "postgres" else SQLITE_DATABASE_URI

# Ensure key directories exist
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)
