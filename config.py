import os
from datetime import timedelta

class Config:
    """
    Final Master Configuration for KaagazSeva.
    Pulls credentials from Render Environment Variables.
    """
    
    # 1. APP CORE
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-this-to-a-secure-random-string')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    # 2. DATABASE (Supabase / Postgres)
    # Render provides DATABASE_URL. We ensure it starts with postgresql:// for SQLAlchemy.
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 3. SECURITY & JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-placeholder')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7) # Long-lived for mobile convenience
    JWT_ERROR_MESSAGE_KEY = 'message'

    # 4. AWS S3 (Document Storage)
    AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
    AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
    AWS_BUCKET_NAME = os.environ.get('AWS_BUCKET_NAME')
    AWS_REGION = os.environ.get('AWS_REGION', 'ap-south-1') # Defaulting to Mumbai

    # 5. PAYMENT GATEWAY (Razorpay)
    RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID')
    RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET')

    # 6. EXTERNAL APIS (SMS/OTP)
    SMS_API_KEY = os.environ.get('SMS_API_KEY')
    
    # 7. BUSINESS CONSTANTS
    # These are pulled from constants.py usually, but can be overridden here
    BASE_URL = os.environ.get('BASE_URL', 'https://kaagazseva.com')
