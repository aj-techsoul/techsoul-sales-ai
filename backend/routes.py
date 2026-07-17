"""
==================================================
TechSoul AI
Backend Routes (SaaS & CRM)
==================================================

Handles Flask web routing for SaaS customer portals, admin lead dashboards,
authentication, chat persistence, notification hubs, and analytical stats.
"""

import os
import uuid
import json
import hashlib
import re
import sqlite3
from datetime import datetime
from flask import request, render_template, session, redirect, url_for, send_from_directory, jsonify, make_response
from werkzeug.utils import secure_filename

from chatbot.chatbot import TechSoulChatbot
from backend.services.response import APIResponse
from backend.services.crm import CRMService
from backend.services.database import DatabaseService
from backend.config import PDF_FOLDER

# Create single instances
chatbot = TechSoulChatbot()
crm = CRMService()
db = DatabaseService()

# File upload settings
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {"txt", "pdf", "docx", "xlsx", "zip", "jpg", "png", "jpeg"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ==========================================
# SECURE PASSWORD HASHING (PBKDF2)
# ==========================================

def hash_password(password):
    salt = os.urandom(16)
    pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return salt.hex() + ":" + pwd_hash.hex()

def verify_password(stored_hash, password):
    try:
        salt_hex, hash_hex = stored_hash.split(":")
        salt = bytes.fromhex(salt_hex)
        pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
        return pwd_hash.hex() == hash_hex
    except Exception:
        return False

# ==========================================
# INTERNATIONAL PHONE VALIDATION
# ==========================================

def validate_international_phone(phone):
    phone = phone.strip()
    try:
        import phonenumbers
        parsed = phonenumbers.parse(phone, None)
        return phonenumbers.is_valid_number(parsed)
    except Exception:
        # Regex fallback: Starts with +, followed by 7-15 digits
        clean_phone = re.sub(r"[\s\-()]+", "", phone)
        return bool(re.match(r"^\+\d{7,15}$", clean_phone))

def format_international_phone(phone):
    phone = phone.strip()
    try:
        import phonenumbers
        parsed = phonenumbers.parse(phone, None)
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except Exception:
        clean_phone = re.sub(r"[\s\-()]+", "", phone)
        if not clean_phone.startswith("+"):
            clean_phone = "+" + clean_phone
        return clean_phone

# ==========================================
# REGISTER ROUTES
# ==========================================

def register_routes(app):
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "techsoul_secret_key_987")

    # ==========================================
    # MIDDLEWARE / BEFORE REQUEST
    # ==========================================

    @app.before_request
    def ensure_guest_session():
        # Ensure rate limiting tracker in session
        if "rate_limit" not in session:
            session["rate_limit"] = []
        
        # Implement a basic rolling rate limiter: Max 60 requests per minute
        now = datetime.now().timestamp()
        rate_list = [t for t in session["rate_limit"] if now - t < 60]
        rate_list.append(now)
        session["rate_limit"] = rate_list
        if len(rate_list) > 60 and request.endpoint in ["chat", "start_chat", "login", "register"]:
            return make_response(jsonify({"success": False, "message": "Too many requests. Please try again in a minute."}), 429)

        # Handle Guest Session ID
        if "session_id" not in session and "user_id" not in session:
            session["session_id"] = str(uuid.uuid4())

    # ==========================================
    # GUEST TO USER MERGE HELPERS
    # ==========================================

    def merge_guest_data(user_id, guest_session_id):
        if not guest_session_id:
            return
        with db.get_connection() as conn:
            cursor = conn.cursor()
            # Update chats to belong to user_id
            cursor.execute(
                "UPDATE chats SET user_id = ?, session_id = NULL WHERE session_id = ?",
                (user_id, guest_session_id)
            )
            # Update uploaded files to belong to user_id
            cursor.execute(
                "UPDATE files SET user_id = ? WHERE user_id IS NULL AND filepath LIKE ?",
                (user_id, f"%{guest_session_id}%")
            )
            conn.commit()



    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username_or_email = request.form.get("username", "").strip()
            password = request.form.get("password", "")

            # Check admin
            admin_user = os.getenv("ADMIN_USERNAME", "admin")
            admin_pass = os.getenv("ADMIN_PASSWORD", "admin123")
            if username_or_email == admin_user and password == admin_pass:
                session["admin_logged_in"] = True
                session["role"] = "admin"
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT id, theme FROM users WHERE role = 'admin'")
                    admin_row = cursor.fetchone()
                    if admin_row:
                        session["user_id"] = admin_row["id"]
                        session["theme"] = admin_row["theme"] if admin_row["theme"] else "blue"
                    else:
                        session["theme"] = "blue"
                return redirect(url_for("admin_dashboard"))

            # Check customer in database
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE email = ? AND role = 'client'", (username_or_email,))
                user = cursor.fetchone()
                if user and verify_password(user["password_hash"], password):
                    session["user_id"] = user["id"]
                    session["user_name"] = user["name"]
                    session["user_email"] = user["email"]
                    session["role"] = "client"
                    session["theme"] = user["theme"] if ("theme" in user.keys() and user["theme"]) else "blue"

                    # Update last login
                    cursor.execute(
                        "UPDATE users SET last_login = ? WHERE id = ?",
                        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user["id"])
                    )
                    conn.commit()

                    # Merge guest chats
                    guest_session = session.pop("session_id", None)
                    merge_guest_data(user["id"], guest_session)

                    return redirect(url_for("customer_dashboard"))
                else:
                    return render_template("login.html", error="Invalid Username/Email or Password.")

        return render_template("login.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            company = request.form.get("company", "").strip()
            email = request.form.get("email", "").strip()
            phone = request.form.get("phone", "").strip()
            password = request.form.get("password", "")

            if not name or not email or not password:
                return render_template("register.html", error="Required fields are missing.")

            # Validate phone if present
            if phone and not validate_international_phone(phone):
                return render_template("register.html", error="Invalid phone number format.")

            pwd_hash = hash_password(password)

            with db.get_connection() as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        """
                        INSERT INTO users (name, company, email, phone, password_hash, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (name, company, email, format_international_phone(phone) if phone else "", pwd_hash, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    )
                    user_id = cursor.lastrowid
                    conn.commit()
                except sqlite3.IntegrityError:
                    return render_template("register.html", error="An account with this email already exists.")

            # Log in the user immediately
            session["user_id"] = user_id
            session["user_name"] = name
            session["user_email"] = email
            session["role"] = "client"
            session["theme"] = "blue"

            # Create welcome notification
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO notifications (user_id, title, message, created_at) VALUES (?, ?, ?, ?)",
                    (user_id, "Welcome to TechSoul AI!", "We are thrilled to help you consult and scale your business solutions.", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                )
                conn.commit()

            # Merge guest data
            guest_session = session.pop("session_id", None)
            merge_guest_data(user_id, guest_session)

            return redirect(url_for("customer_dashboard"))

        return render_template("register.html")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("index"))

    @app.route("/dashboard")
    def customer_dashboard():
        if "user_id" not in session:
            return redirect(url_for("login"))
        return render_template("dashboard.html")

    @app.route("/admin")
    def admin_dashboard():
        if not session.get("admin_logged_in"):
            return redirect(url_for("login"))
        return render_template("admin.html")

    # ==========================================
    # CUSTOMER ACCOUNT & PROFILE API
    # ==========================================

    @app.route("/api/auth/profile", methods=["POST"])
    def update_profile():
        if "user_id" not in session:
            return APIResponse.error("Unauthorized access.", status=401)
        
        user_id = session["user_id"]
        data = request.get_json()
        if not data:
            return APIResponse.error("No data received.")

        name = data.get("name", "").strip()
        company = data.get("company", "").strip()
        phone = data.get("phone", "").strip()
        business_type = data.get("business_type", "").strip()
        website = data.get("website", "").strip()
        address = data.get("address", "").strip()
        country = data.get("country", "").strip()

        if not name:
            return APIResponse.error("Name is required.")
        if phone and not validate_international_phone(phone):
            return APIResponse.error("Invalid phone number format.")

        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE users
                SET name = ?, company = ?, phone = ?, business_type = ?, website = ?, address = ?, country = ?
                WHERE id = ?
                """,
                (name, company, format_international_phone(phone) if phone else "", business_type, website, address, country, user_id)
            )
            conn.commit()

        session["user_name"] = name
        return APIResponse.success(message="Profile updated successfully.")

    @app.route("/api/auth/theme", methods=["POST"])
    def update_theme():
        data = request.get_json() or {}
        theme = data.get("theme", "blue").strip()
        
        if "user_id" in session:
            user_id = session["user_id"]
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET theme = ? WHERE id = ?",
                    (theme, user_id)
                )
                conn.commit()
        
        session["theme"] = theme
        return APIResponse.success(message="Theme updated successfully.", data={"theme": theme})

    # ==========================================
    # DASHBOARD DATA SUMMARY APIS
    # ==========================================

    @app.route("/api/dashboard/summary", methods=["GET"])
    def get_dashboard_summary():
        if "user_id" not in session:
            return APIResponse.error("Unauthorized.", status=401)
        
        user_id = session["user_id"]
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Profile
            cursor.execute("SELECT name, company, email, phone, business_type, website, address, country, theme FROM users WHERE id = ?", (user_id,))
            profile = dict(cursor.fetchone() or {})

            # Projects
            cursor.execute(
                """
                SELECT p.id as project_id, p.name, p.status, p.budget, p.timeline, p.created_at,
                       pr.pdf_file, pr.executive_summary
                FROM projects p
                LEFT JOIN proposals pr ON pr.project_id = p.id
                WHERE p.user_id = ?
                ORDER BY p.id DESC
                """, (user_id,)
            )
            projects_rows = cursor.fetchall()
            projects = []
            for r in projects_rows:
                projects.append({
                    "project_id": f"TS-{r['project_id']:04d}",
                    "name": r["name"],
                    "status": r["status"],
                    "budget": r["budget"],
                    "timeline": r["timeline"],
                    "created_at": r["created_at"],
                    "pdf_file": r["pdf_file"],
                    "executive_summary": r["executive_summary"]
                })

            # Invoices Payments
            cursor.execute(
                """
                SELECT pay.id, pay.amount, pay.stage, pay.status, pay.created_at, pr.name as project_name
                FROM payments pay
                JOIN projects pr ON pay.project_id = pr.id
                WHERE pr.user_id = ?
                ORDER BY pay.id DESC
                """, (user_id,)
            )
            payments = [dict(r) for r in cursor.fetchall()]

            # Notifications
            cursor.execute(
                "SELECT id, title, message, read_status, created_at FROM notifications WHERE user_id = ? ORDER BY id DESC LIMIT 20",
                (user_id,)
            )
            notifications = [dict(r) for r in cursor.fetchall()]

            # Chats
            cursor.execute(
                "SELECT id, title, updated_at FROM chats WHERE user_id = ? ORDER BY id DESC",
                (user_id,)
            )
            chats = [dict(r) for r in cursor.fetchall()]

        return APIResponse.success(
            message="Summary loaded.",
            data={
                "profile": profile,
                "projects": projects,
                "payments": payments,
                "notifications": notifications,
                "chats": chats
            }
        )

    # ==========================================
    # NOTIFICATION READ API
    # ==========================================

    @app.route("/api/notifications/<int:notif_id>/read", methods=["POST"])
    def read_notification(notif_id):
        if "user_id" not in session:
            return APIResponse.error("Unauthorized.", status=401)
        
        user_id = session["user_id"]
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE notifications SET read_status = 1 WHERE id = ? AND user_id = ?",
                (notif_id, user_id)
            )
            conn.commit()
        return APIResponse.success(message="Notification read.")

    # ==========================================
    # CHATS PERSISTENCE APIS
    # ==========================================

    @app.route("/api/chats", methods=["GET"])
    def list_chats():
        user_id = session.get("user_id")
        guest_sess = session.get("session_id")
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            if user_id:
                cursor.execute("SELECT id, title, updated_at FROM chats WHERE user_id = ? ORDER BY id DESC", (user_id,))
            else:
                cursor.execute("SELECT id, title, updated_at FROM chats WHERE session_id = ? ORDER BY id DESC", (guest_sess,))
            
            chats = [dict(r) for r in cursor.fetchall()]
        return APIResponse.success(data={"chats": chats})

    @app.route("/api/chats/new", methods=["POST"])
    def new_chat():
        user_id = session.get("user_id")
        guest_sess = session.get("session_id")
        
        welcome_back_info = None
        if user_id:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, name, company, email, phone, business_type, country, website, address FROM users WHERE id = ?",
                    (user_id,)
                )
                row = cursor.fetchone()
                if row:
                    profile_data = {
                        "name": row["name"] or "",
                        "company": row["company"] or "",
                        "email": row["email"] or "",
                        "phone": row["phone"] or "",
                        "business_type": row["business_type"] or "",
                        "country": row["country"] or "",
                        "website": row["website"] or "",
                        "address": row["address"] or ""
                    }
                    cursor.execute(
                        "SELECT name FROM projects WHERE user_id = ? ORDER BY id DESC LIMIT 1",
                        (user_id,)
                    )
                    prev_proj_row = cursor.fetchone()
                    prev_project = prev_proj_row[0] if prev_proj_row else None
                    
                    welcome_back_info = {
                        "user_id": user_id,
                        "profile": profile_data,
                        "prev_project": prev_project
                    }

        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO chats (user_id, session_id, title, state_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (user_id, guest_sess if not user_id else None, "New Consultation", "{}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            chat_id = cursor.lastrowid
            conn.commit()
        
        session["active_chat_id"] = chat_id
        chatbot.reset()
        response = chatbot.start(welcome_back_info)
        chatbot.conversation.save_session(chat_id)

        # Write firstbot response
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO messages (chat_id, role, content, created_at) VALUES (?, ?, ?, ?)",
                (chat_id, "bot", response["reply"], datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            conn.commit()

        response["chat_id"] = chat_id
        response["client"] = chatbot.get_client()
        return APIResponse.success(data=response)

    @app.route("/api/chats/<int:chat_id>/messages", methods=["GET"])
    def get_messages(chat_id):
        user_id = session.get("user_id")
        guest_sess = session.get("session_id")

        with db.get_connection() as conn:
            cursor = conn.cursor()
            # Security check: User owns this chat
            if user_id:
                cursor.execute("SELECT id FROM chats WHERE id = ? AND user_id = ?", (chat_id, user_id))
            else:
                cursor.execute("SELECT id FROM chats WHERE id = ? AND session_id = ?", (chat_id, guest_sess))
            
            if not cursor.fetchone():
                return APIResponse.error("Access denied.", status=403)

            cursor.execute("SELECT role, content, created_at FROM messages WHERE chat_id = ? ORDER BY id ASC", (chat_id,))
            messages = [dict(r) for r in cursor.fetchall()]

        return APIResponse.success(data={"messages": messages})

    @app.route("/api/chats/<int:chat_id>/rename", methods=["POST"])
    def rename_chat(chat_id):
        user_id = session.get("user_id")
        guest_sess = session.get("session_id")
        data = request.get_json()
        new_title = data.get("title", "").strip() if data else ""
        if not new_title:
            return APIResponse.error("Title cannot be empty.")

        with db.get_connection() as conn:
            cursor = conn.cursor()
            if user_id:
                cursor.execute("UPDATE chats SET title = ? WHERE id = ? AND user_id = ?", (new_title, chat_id, user_id))
            else:
                cursor.execute("UPDATE chats SET title = ? WHERE id = ? AND session_id = ?", (new_title, chat_id, guest_sess))
            conn.commit()

        return APIResponse.success(message="Chat renamed.")

    @app.route("/api/chats/<int:chat_id>/delete", methods=["POST"])
    def delete_chat(chat_id):
        user_id = session.get("user_id")
        guest_sess = session.get("session_id")

        with db.get_connection() as conn:
            cursor = conn.cursor()
            if user_id:
                cursor.execute("DELETE FROM chats WHERE id = ? AND user_id = ?", (chat_id, user_id))
            else:
                cursor.execute("DELETE FROM chats WHERE id = ? AND session_id = ?", (chat_id, guest_sess))
            conn.commit()

        if session.get("active_chat_id") == chat_id:
            session.pop("active_chat_id", None)

        return APIResponse.success(message="Chat deleted.")

    @app.route("/api/chats/<int:chat_id>/continue", methods=["POST"])
    def continue_chat(chat_id):
        user_id = session.get("user_id")
        guest_sess = session.get("session_id")

        with db.get_connection() as conn:
            cursor = conn.cursor()
            if user_id:
                cursor.execute("SELECT id, state_json FROM chats WHERE id = ? AND user_id = ?", (chat_id, user_id))
            else:
                cursor.execute("SELECT id, state_json FROM chats WHERE id = ? AND session_id = ?", (chat_id, guest_sess))
            
            chat = cursor.fetchone()
            if not chat:
                return APIResponse.error("Access denied.", status=403)

        session["active_chat_id"] = chat_id
        chatbot.conversation.load_session(chat_id)
        
        return APIResponse.success(
            message="Chat continued.",
            data={
                "chat_id": chat_id,
                "state": chatbot.get_state_string(),
                "client": chatbot.get_client()
            }
        )

    # ==========================================
    # OVERRIDE START CHAT API
    # ==========================================

    @app.route("/api/start", methods=["GET"])
    def start_chat():
        # Check if there's already an active chat session
        active_chat_id = session.get("active_chat_id")
        if active_chat_id:
            chatbot.conversation.load_session(active_chat_id)
            return APIResponse.success(
                message="Active chat restored.",
                data={
                    "reply": "Restored previous session.",
                    "completed": False,
                    "quotation": None,
                    "proposal": None,
                    "state": chatbot.get_state_string(),
                    "chat_id": active_chat_id,
                    "client": chatbot.get_client()
                }
            )

        # Otherwise create a new chat session automatically
        return new_chat()

    # ==========================================
    # OVERRIDE CHAT MESSAGE API
    # ==========================================

    @app.route("/api/chat", methods=["POST"])
    def chat():
        data = request.get_json()
        if not data:
            return APIResponse.error("No request data received.")

        message = data.get("message", "").strip()
        if message == "":
            return APIResponse.error("Message cannot be empty.")

        # Ensure active chat exists
        active_chat_id = session.get("active_chat_id")
        if not active_chat_id:
            # Create a chat session silently
            user_id = session.get("user_id")
            guest_sess = session.get("session_id")
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO chats (user_id, session_id, title, state_json, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (user_id, guest_sess if not user_id else None, "Consultation", "{}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                )
                active_chat_id = cursor.lastrowid
                conn.commit()
            session["active_chat_id"] = active_chat_id

        # Load chatbot state from SQLite
        chatbot.conversation.load_session(active_chat_id)
        if session.get("user_id"):
            chatbot.conversation.user_id = session.get("user_id")
            # Seed profile details into memory if present
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name, company, email, phone, business_type, country, website, address FROM users WHERE id = ?", (session["user_id"],))
                u_row = cursor.fetchone()
                if u_row:
                    for k in ["name", "company", "email", "phone", "business_type", "country", "website", "address"]:
                        if u_row[k] and not chatbot.conversation.memory.get(k):
                            chatbot.conversation.memory.set(k, u_row[k])

        # Log user message
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO messages (chat_id, role, content, created_at) VALUES (?, ?, ?, ?)",
                (active_chat_id, "user", message, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            conn.commit()

        # Generate response
        response = chatbot.reply(message)

        # Extract reply text
        if isinstance(response, dict):
            reply_text = response.get("reply", "")
        else:
            reply_text = response

        # Log bot reply
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO messages (chat_id, role, content, created_at) VALUES (?, ?, ?, ?)",
                (active_chat_id, "bot", reply_text, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            conn.commit()

        # Update chat session state
        chatbot.conversation.save_session(active_chat_id)

        # If project completed, sync references
        if isinstance(response, dict) and response.get("completed"):
            response["chat_id"] = active_chat_id
            response["client"] = chatbot.get_client()
            return APIResponse.success(data=response)

        # Sync and return
        response_data = response if isinstance(response, dict) else {"reply": response}
        response_data["chat_id"] = active_chat_id
        response_data["client"] = chatbot.get_client()
        return APIResponse.success(data=response_data)

    # ==========================================
    # OVERRIDE RESET CHAT API
    # ==========================================

    @app.route("/api/reset", methods=["POST"])
    def reset_chat():
        chatbot.reset()
        session.pop("active_chat_id", None)
        return APIResponse.success(message="Conversation reset.")

    # ==========================================
    # OVERRIDE STATUS / CURRENT STATE API
    # ==========================================

    @app.route("/api/status", methods=["GET"])
    def status():
        active_chat_id = session.get("active_chat_id")
        if active_chat_id:
            chatbot.conversation.load_session(active_chat_id)
        return APIResponse.success(
            data={
                "state": chatbot.get_state_string(),
                "client": chatbot.get_client(),
                "chat_id": active_chat_id,
                "role": session.get("role", "guest"),
                "user_name": session.get("user_name", "")
            }
        )

    # ==========================================
    # FILE UPLOADS API
    # ==========================================

    @app.route("/api/upload", methods=["POST"])
    def upload_file():
        if "file" not in request.files:
            return APIResponse.error("No file part in the request.")

        file = request.files["file"]
        if file.filename == "":
            return APIResponse.error("No file selected.")

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add uuid prefix to guarantee uniqueness and prevent path traversal
            unique_filename = f"{uuid.uuid4()}_{filename}"
            filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
            file.save(filepath)

            # Log file in database
            user_id = session.get("user_id")
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO files (user_id, filename, filepath, filetype, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (user_id, filename, filepath, file.content_type, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                )
                conn.commit()

            # Read file requirements if it is PDF, DOCX, XLSX, ZIP or text-based, and feed it to chat memory!
            file_content = ""
            if filename.endswith(".txt") or filename.endswith(".json"):
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        file_content = f.read()
                except Exception:
                    pass
            elif filename.endswith(".pdf"):
                try:
                    import pypdf
                    reader = pypdf.PdfReader(filepath)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() or ""
                    file_content = text
                except Exception as e:
                    print(f"Error reading PDF upload: {e}")
            elif filename.endswith(".docx"):
                try:
                    import docx
                    doc = docx.Document(filepath)
                    text = "\n".join([p.text for p in doc.paragraphs])
                    file_content = text
                except Exception as e:
                    print(f"Error reading DOCX upload: {e}")
            elif filename.endswith(".xlsx"):
                try:
                    import openpyxl
                    wb = openpyxl.load_workbook(filepath, read_only=True)
                    text = ""
                    for sheet in wb.sheetnames:
                        ws = wb[sheet]
                        for row in ws.iter_rows(values_only=True):
                            text += " ".join([str(cell) for cell in row if cell is not None]) + "\n"
                    file_content = text
                except Exception as e:
                    print(f"Error reading Excel upload: {e}")
            elif filename.endswith(".zip"):
                try:
                    import zipfile
                    with zipfile.ZipFile(filepath, 'r') as zip_ref:
                        file_content = "ZIP archive files list: " + ", ".join(zip_ref.namelist())
                except Exception as e:
                    print(f"Error reading ZIP upload: {e}")

            if file_content:
                active_chat_id = session.get("active_chat_id")
                if active_chat_id:
                    chatbot.conversation.load_session(active_chat_id)
                    
                    # Extract requirements using Gemini
                    try:
                        from backend.services.gemini_service import GeminiService
                        gemini_svc = GeminiService()
                        prompt = f"""
                        Analyze the following text extracted from an uploaded client document.
                        Identify and extract any project parameters such as:
                        - Project Type (e.g. E-Commerce, Mobile App, Business Website, CRM, ERP, AI Solution, Custom Software)
                        - Features (e.g. Login, Dashboard, Admin Panel, Payment Gateway, Inventory, Reports, Notifications, Analytics, API Integration, AI Chatbot, Multi Language)
                        - Budget (e.g. $10,000, 2 Lakhs)
                        - Timeline (e.g. 3 months, Urgent, Fast, Normal)
                        
                        Text content:
                        {file_content[:3000]}
                        
                        Return your findings ONLY as a JSON object:
                        {{
                          "project": "project type or empty",
                          "features": ["feature 1", "feature 2"],
                          "budget": "budget or empty",
                          "timeline": "timeline or empty"
                        }}
                        """
                        result = gemini_svc.generate(prompt)
                        if result.startswith("```"):
                            result = re.sub(r"^```(?:json)?\n", "", result)
                            result = re.sub(r"\n```$", "", result)
                        
                        data = json.loads(result.strip())
                        # Update chatbot conversation memory!
                        for k, v in data.items():
                            if v:
                                if k == "features" and isinstance(v, list):
                                    for f in v:
                                        chatbot.conversation.memory.add_feature(f)
                                else:
                                    chatbot.conversation.memory.set(k, v)
                                    
                        # Save chatbot state
                        chatbot.conversation.save_session(active_chat_id)
                    except Exception as ex:
                        print(f"Error parsing requirements with Gemini: {ex}")

            return APIResponse.success(
                message="File uploaded successfully.",
                data={"filename": filename}
            )

        return APIResponse.error("File extension not allowed.")

    @app.route("/api/files", methods=["GET"])
    def list_files():
        if "user_id" not in session:
            return APIResponse.error("Unauthorized.", status=401)
        
        user_id = session["user_id"]
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT filename, created_at FROM files WHERE user_id = ? ORDER BY id DESC", (user_id,))
            files = [dict(r) for r in cursor.fetchall()]
        return APIResponse.success(data={"files": files})

    # ==========================================
    # PROPOSAL DOWNLOAD FOR CLIENTS
    # ==========================================

    @app.route("/api/proposal/download/<filename>", methods=["GET"])
    def download_proposal(filename):
        filename = os.path.basename(filename)
        return send_from_directory(PDF_FOLDER, filename, as_attachment=True)

    # ==========================================
    # BLUEPRINT DOWNLOAD FOR CLIENTS
    # ==========================================

    @app.route("/api/blueprint/download/pdf/<lead_id>", methods=["GET"])
    def download_blueprint_pdf(lead_id):
        lead_id = os.path.basename(lead_id)
        filename = f"blueprint_{lead_id}.pdf"
        return send_from_directory(PDF_FOLDER, filename, as_attachment=True)

    @app.route("/api/blueprint/download/docx/<lead_id>", methods=["GET"])
    def download_blueprint_docx(lead_id):
        lead_id = os.path.basename(lead_id)
        filename = f"blueprint_{lead_id}.docx"
        return send_from_directory(PDF_FOLDER, filename, as_attachment=True)

    # ==========================================
    # CRM API LIST LEADS
    # ==========================================

    @app.route("/api/admin/leads", methods=["GET"])
    def list_leads():
        if not session.get("admin_logged_in"):
            return APIResponse.error("Unauthorized access.", status=401)
        leads = crm.get_all_clients()
        return APIResponse.success(
            message="Leads retrieved.",
            data={"leads": leads}
        )

    # ==========================================
    # CRM API UPDATE STATUS
    # ==========================================

    @app.route("/api/admin/leads/<lead_id>/status", methods=["POST"])
    def update_lead_status(lead_id):
        if not session.get("admin_logged_in"):
            return APIResponse.error("Unauthorized access.", status=401)

        data = request.get_json()
        if not data or "status" not in data:
            return APIResponse.error("Status field is required.")

        new_status = data["status"]
        success = crm.update_status(lead_id, new_status)
        if success:
            return APIResponse.success(message=f"Status updated to '{new_status}' successfully.")
        return APIResponse.error("Lead ID not found.")

    # ==========================================
    # CRM API ANALYTICS STATS
    # ==========================================

    @app.route("/api/admin/stats", methods=["GET"])
    def get_stats():
        if not session.get("admin_logged_in"):
            return APIResponse.error("Unauthorized access.", status=401)

        leads = crm.get_all_clients()
        total_leads = len(leads)

        won_leads = [l for l in leads if l.get("status") == "Won"]
        lost_leads = [l for l in leads if l.get("status") == "Lost"]
        pipeline_leads = [l for l in leads if l.get("status") not in ["Won", "Lost"]]

        total_revenue = sum(l.get("quotation", {}).get("total", 0) for l in won_leads)
        pipeline_revenue = sum(l.get("quotation", {}).get("total", 0) for l in pipeline_leads)

        conversion_rate = round((len(won_leads) / total_leads * 100)) if total_leads > 0 else 0

        # Group Monthly Revenue (Won leads)
        monthly_rev = {}
        for l in won_leads:
            date_str = l.get("created_at", "")[:7]
            if date_str:
                monthly_rev[date_str] = monthly_rev.get(date_str, 0) + l.get("quotation", {}).get("total", 0)

        sorted_monthly = [{"month": k, "revenue": v} for k, v in sorted(monthly_rev.items())]

        # Group Project Types
        project_types = {}
        for l in leads:
            p_type = l.get("client", {}).get("project", "Other")
            if p_type:
                project_types[p_type] = project_types.get(p_type, 0) + 1

        # Group Popular Features
        feature_counts = {}
        for l in leads:
            features = l.get("client", {}).get("features", [])
            for f in features:
                feature_counts[f] = feature_counts.get(f, 0) + 1

        sorted_features = [{"feature": k, "count": v} for k, v in sorted(feature_counts.items(), key=lambda x: x[1], reverse=True)[:5]]

        # Group Lead Statuses
        status_counts = {}
        for l in leads:
            status = l.get("status", "New Lead")
            status_counts[status] = status_counts.get(status, 0) + 1

        return APIResponse.success(
            message="Statistics computed.",
            data={
                "kpis": {
                    "total_leads": total_leads,
                    "won_deals": len(won_leads),
                    "lost_deals": len(lost_leads),
                    "pipeline_deals": len(pipeline_leads),
                    "revenue": total_revenue,
                    "pipeline_value": pipeline_revenue,
                    "conversion_rate": conversion_rate
                },
                "monthly_revenue": sorted_monthly,
                "project_types": project_types,
                "popular_features": sorted_features,
                "status_counts": status_counts
            }
        )

    # ==========================================
    # BUDGET SIMULATOR API
    # ==========================================

    @app.route("/api/simulator/recalculate", methods=["GET"])
    def api_simulate_budget():
        from backend.services.pricing import PricingService
        pricing = PricingService()
        budget = request.args.get("budget", "50000")
        project = request.args.get("project", "E-Commerce")
        
        # Load active chat memory context to feed AI advisor
        chat_context = None
        active_chat_id = session.get("active_chat_id")
        if active_chat_id:
            try:
                chatbot.conversation.load_session(active_chat_id)
                chat_context = chatbot.conversation.get_client_data()
            except Exception as ex:
                print(f"Error loading chat context for simulation: {ex}")

        try:
            data = pricing.simulate_budget(project, budget, chat_context=chat_context)
            return APIResponse.success(data=data)
        except Exception as e:
            return APIResponse.error(f"Simulator error: {str(e)}")