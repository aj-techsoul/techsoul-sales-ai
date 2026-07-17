"""
==================================================
TechSoul AI
Backend Application
==================================================
"""
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from flask import Flask, render_template
from flask_cors import CORS

from backend.routes import register_routes
from backend.config import HOST, PORT, DEBUG


# ==========================================
# CREATE APPLICATION
# ==========================================

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)

# ==========================================
# ENABLE CORS
# ==========================================

CORS(app)

# ==========================================
# REGISTER API ROUTES
# ==========================================

register_routes(app)

# ==========================================
# FRONTEND ROUTES
# ==========================================

@app.route("/")
def index():
    """
    Load Frontend Dashboard
    """
    return render_template("index.html")


# ==========================================
# HEALTH CHECK
# ==========================================

@app.route("/health")
def health():
    """
    Backend Status
    """
    return {
        "status": "running",
        "application": "TechSoul AI Backend"
    }


# ==========================================
# START SERVER
# ==========================================

if __name__ == "__main__":

    app.run(
        host=HOST,
        port=PORT,
        debug=DEBUG
    )