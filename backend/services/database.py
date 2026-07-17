"""
==================================================
TechSoul AI
Database Service (SQLite)
==================================================

Handles SQLite connection, schema initialization, and migration.
"""

import sqlite3
import os
import json
from datetime import datetime
import hashlib

# Project root path resolution
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "data", "techsoul.db")

class DatabaseService:
    """
    SQLite Database Controller
    """

    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self.init_db()
        self.migrate_old_data()

    def get_connection(self):
        """
        Get sqlite3 database connection.
        """
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """
        Initialize the normalized database schema.
        """
        queries = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                company TEXT,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                password_hash TEXT NOT NULL,
                business_type TEXT,
                website TEXT,
                address TEXT,
                profile_picture TEXT,
                country TEXT,
                status TEXT DEFAULT 'Active',
                role TEXT DEFAULT 'client',
                theme TEXT DEFAULT 'blue',
                created_at TEXT,
                last_login TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                session_id TEXT,
                title TEXT,
                state_json TEXT,
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT,
                FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT NOT NULL,
                status TEXT DEFAULT 'New Lead',
                budget INTEGER DEFAULT 0,
                timeline TEXT,
                lead_score INTEGER DEFAULT 0,
                deal_size INTEGER DEFAULT 0,
                next_follow_up TEXT,
                business_category TEXT,
                proposal_status TEXT DEFAULT 'Proposal Sent',
                interested_features TEXT,
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS quotations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                details_json TEXT NOT NULL,
                created_at TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS proposals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                executive_summary TEXT,
                goals_json TEXT,
                scope TEXT,
                pdf_file TEXT,
                created_at TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                amount INTEGER NOT NULL,
                stage TEXT NOT NULL,
                status TEXT DEFAULT 'Pending',
                created_at TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                read_status INTEGER DEFAULT 0,
                created_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL,
                filetype TEXT,
                created_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            )
            """
        ]

        with self.get_connection() as conn:
            cursor = conn.cursor()
            for query in queries:
                cursor.execute(query)
            
            # Run migrations to add missing columns to existing tables
            cursor.execute("PRAGMA table_info(chats)")
            chats_cols = [row[1] for row in cursor.fetchall()]
            if "state_json" not in chats_cols:
                cursor.execute("ALTER TABLE chats ADD COLUMN state_json TEXT")

            cursor.execute("PRAGMA table_info(users)")
            users_cols = [row[1] for row in cursor.fetchall()]
            for col_name, col_type in [
                ("business_type", "TEXT"),
                ("website", "TEXT"),
                ("address", "TEXT"),
                ("profile_picture", "TEXT"),
                ("country", "TEXT"),
                ("theme", "TEXT DEFAULT 'blue'")
            ]:
                if col_name not in users_cols:
                    cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")

            cursor.execute("PRAGMA table_info(projects)")
            projects_cols = [row[1] for row in cursor.fetchall()]
            for col_name, col_type in [
                ("lead_score", "INTEGER DEFAULT 0"),
                ("deal_size", "INTEGER DEFAULT 0"),
                ("next_follow_up", "TEXT"),
                ("business_category", "TEXT"),
                ("proposal_status", "TEXT DEFAULT 'Proposal Sent'"),
                ("interested_features", "TEXT")
            ]:
                if col_name not in projects_cols:
                    cursor.execute(f"ALTER TABLE projects ADD COLUMN {col_name} {col_type}")

            # Create default admin if not exists
            cursor.execute("SELECT id FROM users WHERE role = 'admin'")
            if not cursor.fetchone():
                admin_user = os.getenv("ADMIN_USERNAME", "admin")
                admin_pass = os.getenv("ADMIN_PASSWORD", "admin123")
                pwd_hash = hashlib.sha256(admin_pass.encode()).hexdigest()
                cursor.execute(
                    """
                    INSERT INTO users (name, email, password_hash, role, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    ("Admin", f"{admin_user}@techsoul.ai", pwd_hash, "admin", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                )
            conn.commit()

    def migrate_old_data(self):
        """
        Migrate old JSON data (clients.json) into SQLite.
        """
        clients_json_path = os.path.join(BASE_DIR, "data", "clients.json")
        if not os.path.exists(clients_json_path):
            return

        try:
            with open(clients_json_path, "r", encoding="utf-8") as file:
                leads = json.load(file)
        except Exception:
            return

        if not leads:
            return

        with self.get_connection() as conn:
            cursor = conn.cursor()
            for lead in leads:
                client_data = lead.get("client") or {}
                email = client_data.get("email")
                if not email:
                    continue

                # Check if user already exists
                cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
                user = cursor.fetchone()
                if user:
                    user_id = user[0]
                else:
                    # Create new user
                    # Default placeholder password
                    dummy_pass = "user123"
                    pwd_hash = hashlib.sha256(dummy_pass.encode()).hexdigest()
                    cursor.execute(
                        """
                        INSERT INTO users (name, company, email, phone, password_hash, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            client_data.get("name", "Migrated Lead"),
                            client_data.get("company", ""),
                            email,
                            client_data.get("phone", ""),
                            pwd_hash,
                            lead.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        )
                    )
                    user_id = cursor.lastrowid

                # Create project for the user
                project_name = client_data.get("project", "Consultation Project")
                cursor.execute(
                    """
                    SELECT id FROM projects WHERE user_id = ? AND name = ?
                    """,
                    (user_id, project_name)
                )
                project = cursor.fetchone()
                if project:
                    project_id = project[0]
                else:
                    cursor.execute(
                        """
                        INSERT INTO projects (user_id, name, status, budget, timeline, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            user_id,
                            project_name,
                            lead.get("status", "New Lead"),
                            self._clean_budget(client_data.get("budget", 0)),
                            client_data.get("timeline", "Normal"),
                            lead.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                            lead.get("updated_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        )
                    )
                    project_id = cursor.lastrowid

                # Create quotation
                quotation_data = lead.get("quotation") or {}
                if quotation_data:
                    cursor.execute(
                        "SELECT id FROM quotations WHERE project_id = ?",
                        (project_id,)
                    )
                    if not cursor.fetchone():
                        cursor.execute(
                            """
                            INSERT INTO quotations (project_id, details_json, created_at)
                            VALUES (?, ?, ?)
                            """,
                            (
                                project_id,
                                json.dumps(quotation_data),
                                lead.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                            )
                        )

                # Create proposal
                proposal_data = lead.get("proposal") or {}
                if proposal_data:
                    cursor.execute(
                        "SELECT id FROM proposals WHERE project_id = ?",
                        (project_id,)
                    )
                    if not cursor.fetchone():
                        cursor.execute(
                            """
                            INSERT INTO proposals (project_id, executive_summary, goals_json, scope, pdf_file, created_at)
                            VALUES (?, ?, ?, ?, ?, ?)
                            """,
                            (
                                project_id,
                                proposal_data.get("executive_summary", ""),
                                json.dumps(proposal_data.get("goals", [])),
                                proposal_data.get("scope", ""),
                                proposal_data.get("pdf_file", ""),
                                lead.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                            )
                        )

            conn.commit()

        # Delete/Rename old file to prevent repeated migrations
        try:
            os.rename(clients_json_path, clients_json_path + ".bak")
        except Exception:
            pass

    def _clean_budget(self, budget):
        if isinstance(budget, (int, float)):
            return int(budget)
        budget_str = str(budget).lower().replace(",", "").replace("₹", "").replace("$", "").strip()
        import re
        match = re.search(r'(\d+)', budget_str)
        if match:
            return int(match.group(1))
        return 0