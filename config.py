# backend/config.py

import os
from dotenv import load_dotenv
from datetime import timedelta

# Load environment variables from .env
load_dotenv()

# ---------------- FLASK CORE ----------------
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "kaagazseva-dev-secret")

# ---------------- JWT CONFIG ----------------
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "ks-jwt-secret-2026")
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

# ---------------- FILE UPLOAD ----------------
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB

# ---------------- RAZORPAY ----------------
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

# ---------------- PLATFORM SETTINGS ----------------
AGENT_COMMISSION_PERCENT = float(os.getenv("AGENT_COMMISSION_PERCENT", "0.70"))
MAX_AGENT_LOAD = int(os.getenv("MAX_AGENT_LOAD", "20"))

# ---------------- RATE LIMIT DEFAULTS ----------------
DEFAULT_RATE_LIMIT_DAY = "200 per day"
DEFAULT_RATE_LIMIT_HOUR = "50 per hour"

# ---------------- ADMIN SECURITY ----------------
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "super-secret-admin-key")
