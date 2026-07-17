"""
==================================================
TechSoul AI
Backend Configuration
==================================================

Stores all application settings.
"""

import os


# ==================================================
# PROJECT ROOT
# ==================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)


# ==================================================
# FLASK SETTINGS
# ==================================================

HOST = "0.0.0.0"

PORT = 5000

DEBUG = True


# ==================================================
# DATA FOLDER
# ==================================================

DATA_FOLDER = os.path.join(BASE_DIR, "data")

os.makedirs(DATA_FOLDER, exist_ok=True)


# ==================================================
# DATABASE FILES
# ==================================================

CLIENT_DATABASE = os.path.join(
    DATA_FOLDER,
    "clients.json"
)

PRICING_DATABASE = os.path.join(
    DATA_FOLDER,
    "pricing.json"
)

QUOTE_DATABASE = os.path.join(
    DATA_FOLDER,
    "quotes.json"
)

PROPOSAL_DATABASE = os.path.join(
    DATA_FOLDER,
    "proposals.json"
)


# ==================================================
# PDF STORAGE
# ==================================================

PDF_FOLDER = os.path.join(
    DATA_FOLDER,
    "proposals"
)

os.makedirs(PDF_FOLDER, exist_ok=True)


# ==================================================
# COMPANY DETAILS
# ==================================================

COMPANY_NAME = "TechSoul AI"

COMPANY_TAGLINE = "Building Intelligent Digital Solutions"

COMPANY_EMAIL = "info@techsoulai.com"

COMPANY_PHONE = "+91-9876543210"

COMPANY_WEBSITE = "www.techsoulai.com"

COMPANY_ADDRESS = "Guwahati, Assam, India"

CURRENCY = "₹"


# ==================================================
# CHATBOT SETTINGS
# ==================================================

DEFAULT_STATE = "WELCOME"

MAX_FEATURES = 20

SESSION_TIMEOUT = 30


# ==================================================
# EMAIL SETTINGS
# ==================================================

EMAIL_HOST = "smtp.gmail.com"

EMAIL_PORT = 587

EMAIL_ADDRESS = "yourcompany@gmail.com"

EMAIL_PASSWORD = "YOUR_APP_PASSWORD"


# ==================================================
# CRM SETTINGS
# ==================================================

DEFAULT_LEAD_STATUS = "New Lead"

LEAD_STATUSES = [

    "New Lead",

    "Contacted",

    "Proposal Sent",

    "Negotiation",

    "Won",

    "Lost"

]


# ==================================================
# PROPOSAL SETTINGS
# ==================================================

PROPOSAL_VALIDITY_DAYS = 30

DEFAULT_WARRANTY = "30 Days"

DEFAULT_SUPPORT = "Email & Phone"

DEFAULT_PAYMENT_PLAN = [

    {
        "stage": "Advance",
        "percentage": 50
    },

    {
        "stage": "Development",
        "percentage": 30
    },

    {
        "stage": "Deployment",
        "percentage": 20
    }

]


# ==================================================
# AI SETTINGS
# ==================================================

ENABLE_UPSELL = True

ENABLE_BUDGET_OPTIMIZATION = True

ENABLE_PDF_GENERATION = True

ENABLE_EMAIL_SERVICE = True
# ==================================================
# GEMINI AI SETTINGS
# ==================================================

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

GEMINI_MODEL = "gemini-1.5-flash"