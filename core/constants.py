# core/constants.py

# Commission & Financials
PLATFORM_COMMISSION_PERCENT = 20.0  # KaagazSeva takes 20%
AGENT_COMMISSION_PERCENT = 80.0     # Agent takes 80%
TAX_PERCENT = 18.0                  # GST if applicable

# File Upload Constraints
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB Limit
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

# Assignment Logic
MAX_AGENT_WORKLOAD = 20             # Max active applications per agent
SEARCH_RADIUS_KM = 20             # Distance to search for agents

# Auth
OTP_EXPIRY_MINUTES = 10
