import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

SUBMISSIONS_CSV = os.path.join(DATA_DIR, "submissions.csv")
SUBMISSIONS_XLSX = os.path.join(DATA_DIR, "submissions.xlsx")
LOGS_CSV = os.path.join(DATA_DIR, "logs.csv")

SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")

# Email settings (SMTP) - env se load hote hain
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
MAIL_FROM = os.environ.get("MAIL_FROM", SMTP_USER)
OWNER_EMAIL = os.environ.get("OWNER_EMAIL", "")
APP_NAME = os.environ.get("APP_NAME", "AutoFlow")

# Demo mode: email bhejne ke bjaw SMTP_USER set ho toh asli mail jayega
DEMO_MODE = not (SMTP_USER and SMTP_PASS)
