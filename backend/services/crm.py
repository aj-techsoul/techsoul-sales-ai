"""
==================================================
TechSoul AI
CRM Service (SQLite)
==================================================

Handles client lead management using SQLite.
"""

import json
from datetime import datetime
from backend.config import DEFAULT_LEAD_STATUS
from backend.services.database import DatabaseService

class CRMService:
    """
    Customer Relationship Management Service using SQLite
    """

    def __init__(self):
        self.db = DatabaseService()

    def calculate_lead_score(self, client, quotation):
        score = 30 # Base score for engaging
        
        # Budget contribution (max 30 points)
        budget = self._clean_budget(client.get("budget", 0))
        if budget >= 250000:
            score += 30
        elif budget >= 150000:
            score += 20
        elif budget >= 50000:
            score += 10
        else:
            score += 5
            
        # Timeline urgency (max 20 points)
        timeline = client.get("timeline", "Normal")
        if timeline == "Urgent":
            score += 20
        elif timeline == "Fast":
            score += 10
        else:
            score += 5
            
        # Features score (max 20 points)
        features = client.get("features", [])
        score += min(len(features) * 3, 20)
        
        # Profile completeness contribution (max 10 points)
        if client.get("phone") and client.get("company") and client.get("email"):
            score += 10
            
        return min(score, 100)

    def get_all_clients(self):
        """
        Return all leads.
        """
        leads = []
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT p.id as project_id, p.name as project_name, p.status, p.budget, p.timeline, p.created_at, p.updated_at,
                       p.lead_score, p.deal_size, p.next_follow_up, p.business_category, p.proposal_status, p.interested_features,
                       u.id as user_id, u.name as client_name, u.company, u.email, u.phone, u.business_type, u.website, u.address, u.country,
                       q.details_json as quotation_json,
                       pr.executive_summary, pr.goals_json, pr.scope, pr.pdf_file
                FROM projects p
                LEFT JOIN users u ON p.user_id = u.id
                LEFT JOIN quotations q ON q.project_id = p.id
                LEFT JOIN proposals pr ON pr.project_id = p.id
                ORDER BY p.id DESC
                """
            )
            rows = cursor.fetchall()
            for r in rows:
                leads.append({
                    "lead_id": f"TS-{r['project_id']:04d}",
                    "created_at": r['created_at'],
                    "updated_at": r['updated_at'],
                    "status": r['status'],
                    "crm_metrics": {
                        "lead_score": r['lead_score'] or 0,
                        "deal_size": r['deal_size'] or 0,
                        "next_follow_up": r['next_follow_up'] or "",
                        "business_category": r['business_category'] or "",
                        "proposal_status": r['proposal_status'] or "",
                        "interested_features": r['interested_features'] or ""
                    },
                    "client": {
                        "name": r['client_name'],
                        "company": r['company'],
                        "email": r['email'],
                        "phone": r['phone'],
                        "project": r['project_name'],
                        "budget": r['budget'],
                        "timeline": r['timeline'],
                        "business_type": r['business_type'],
                        "website": r['website'],
                        "address": r['address'],
                        "country": r['country'] or ""
                    },
                    "quotation": json.loads(r['quotation_json']) if r['quotation_json'] else {},
                    "proposal": {
                        "executive_summary": r['executive_summary'],
                        "goals": json.loads(r['goals_json']) if r['goals_json'] else [],
                        "scope": r['scope'],
                        "pdf_file": r['pdf_file']
                    }
                })
        return leads

    def total_leads(self):
        """
        Return total number of leads.
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM projects")
            return cursor.fetchone()[0]

    def save_client(self, client, quotation, proposal):
        """
        Save a new client lead.
        """
        email = client.get("email")
        if not email:
            return None

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            if user:
                user_id = user[0]
                # Update user profile with latest details
                cursor.execute(
                    """
                    UPDATE users 
                    SET name = ?, company = ?, phone = ?, business_type = ?, website = ?, address = ?, country = ?
                    WHERE id = ?
                    """,
                    (
                        client.get("name"),
                        client.get("company"),
                        client.get("phone"),
                        client.get("business_type"),
                        client.get("website"),
                        client.get("address"),
                        client.get("country"),
                        user_id
                    )
                )
            else:
                # Create user
                import hashlib
                dummy_pass = "user123"
                pwd_hash = hashlib.sha256(dummy_pass.encode()).hexdigest()
                cursor.execute(
                    """
                    INSERT INTO users (name, company, email, phone, password_hash, business_type, website, address, country, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        client.get("name"),
                        client.get("company"),
                        email,
                        client.get("phone"),
                        pwd_hash,
                        client.get("business_type", ""),
                        client.get("website", ""),
                        client.get("address", ""),
                        client.get("country", ""),
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    )
                )
                user_id = cursor.lastrowid

            from datetime import timedelta
            lead_score = self.calculate_lead_score(client, quotation)
            deal_size = quotation.get("total", 0)
            next_follow_up = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
            business_category = client.get("business_type") or client.get("industry") or "General Software"
            interested_features = ", ".join(client.get("features", []))

            # Create project
            project_name = client.get("project", "Consultation Project")
            cursor.execute(
                """
                INSERT INTO projects (user_id, name, status, budget, timeline, lead_score, deal_size, next_follow_up, business_category, proposal_status, interested_features, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    project_name,
                    DEFAULT_LEAD_STATUS,
                    self._clean_budget(client.get("budget", 0)),
                    client.get("timeline", "Normal"),
                    lead_score,
                    deal_size,
                    next_follow_up,
                    business_category,
                    DEFAULT_LEAD_STATUS,
                    interested_features,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
            )
            project_id = cursor.lastrowid

            # Insert quotation
            if quotation:
                cursor.execute(
                    """
                    INSERT INTO quotations (project_id, details_json, created_at)
                    VALUES (?, ?, ?)
                    """,
                    (project_id, json.dumps(quotation), datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                )

            # Insert proposal
            if proposal:
                cursor.execute(
                    """
                    INSERT INTO proposals (project_id, executive_summary, goals_json, scope, pdf_file, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        project_id,
                        proposal.get("executive_summary", ""),
                        json.dumps(proposal.get("goals", [])),
                        proposal.get("scope", ""),
                        proposal.get("pdf_file", ""),
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    )
                )

            # Create advance payment stage (50%)
            if quotation:
                advance_amt = round(quotation.get("total", 0) * 0.5)
                cursor.execute(
                    "INSERT INTO payments (project_id, amount, stage, status, created_at) VALUES (?, ?, ?, ?, ?)",
                    (project_id, advance_amt, "Advance Payment (50%)", "Pending", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                )
            
            # Create completion notification
            cursor.execute(
                "INSERT INTO notifications (user_id, title, message, created_at) VALUES (?, ?, ?, ?)",
                (
                    user_id, 
                    "Proposal & Quotation Ready!", 
                    f"A custom proposal has been generated for your project '{client.get('project')}' with budget ₹{quotation.get('total', 0) if quotation else 0:,}.", 
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
            )

            conn.commit()

            lead = {
                "lead_id": f"TS-{project_id:04d}",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": DEFAULT_LEAD_STATUS,
                "crm_metrics": {
                    "lead_score": lead_score,
                    "deal_size": deal_size,
                    "next_follow_up": next_follow_up,
                    "business_category": business_category,
                    "proposal_status": DEFAULT_LEAD_STATUS,
                    "interested_features": interested_features
                },
                "client": client,
                "quotation": quotation,
                "proposal": proposal
            }
            return lead

    def find_client(self, lead_id):
        """
        Find client by Lead ID (TS-XXXX).
        """
        try:
            project_id = int(lead_id.replace("TS-", ""))
        except ValueError:
            return None

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT p.id as project_id, p.name as project_name, p.status, p.budget, p.timeline, p.created_at, p.updated_at,
                       p.lead_score, p.deal_size, p.next_follow_up, p.business_category, p.proposal_status, p.interested_features,
                       u.id as user_id, u.name as client_name, u.company, u.email, u.phone, u.business_type, u.website, u.address, u.country,
                       q.details_json as quotation_json,
                       pr.executive_summary, pr.goals_json, pr.scope, pr.pdf_file
                FROM projects p
                LEFT JOIN users u ON p.user_id = u.id
                LEFT JOIN quotations q ON q.project_id = p.id
                LEFT JOIN proposals pr ON pr.project_id = p.id
                WHERE p.id = ?
                """,
                (project_id,)
            )
            r = cursor.fetchone()
            if r:
                return {
                    "lead_id": f"TS-{r['project_id']:04d}",
                    "created_at": r['created_at'],
                    "updated_at": r['updated_at'],
                    "status": r['status'],
                    "crm_metrics": {
                        "lead_score": r['lead_score'] or 0,
                        "deal_size": r['deal_size'] or 0,
                        "next_follow_up": r['next_follow_up'] or "",
                        "business_category": r['business_category'] or "",
                        "proposal_status": r['proposal_status'] or "",
                        "interested_features": r['interested_features'] or ""
                    },
                    "client": {
                        "name": r['client_name'],
                        "company": r['company'],
                        "email": r['email'],
                        "phone": r['phone'],
                        "project": r['project_name'],
                        "budget": r['budget'],
                        "timeline": r['timeline'],
                        "business_type": r['business_type'],
                        "website": r['website'],
                        "address": r['address'],
                        "country": r['country'] or ""
                    },
                    "quotation": json.loads(r['quotation_json']) if r['quotation_json'] else {},
                    "proposal": {
                        "executive_summary": r['executive_summary'],
                        "goals": json.loads(r['goals_json']) if r['goals_json'] else [],
                        "scope": r['scope'],
                        "pdf_file": r['pdf_file']
                    }
                }
        return None

    def update_proposal_pdf(self, lead_id, pdf_filename):
        """
        Update the PDF filename for a lead's proposal.
        """
        try:
            project_id = int(lead_id.replace("TS-", ""))
        except ValueError:
            return False

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE proposals SET pdf_file = ? WHERE project_id = ?",
                (pdf_filename, project_id)
            )
            conn.commit()
            return True

    def update_status(self, lead_id, status):
        """
        Update lead status.
        """
        try:
            project_id = int(lead_id.replace("TS-", ""))
        except ValueError:
            return False

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE projects 
                SET status = ?, updated_at = ?
                WHERE id = ?
                """,
                (status, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), project_id)
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete_client(self, lead_id):
        """
        Delete a lead (project).
        """
        try:
            project_id = int(lead_id.replace("TS-", ""))
        except ValueError:
            return False

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            conn.commit()
            return cursor.rowcount > 0

    def search_clients(self, keyword):
        """
        Search leads by name, company, email, or project type.
        """
        leads = self.get_all_clients()
        results = []
        kw = keyword.lower()
        for l in leads:
            c = l["client"]
            if (
                kw in c.get("name", "").lower()
                or kw in c.get("company", "").lower()
                or kw in c.get("email", "").lower()
                or kw in c.get("project", "").lower()
            ):
                results.append(l)
        return results

    def get_clients_by_status(self, status):
        """
        Return all leads with given status.
        """
        leads = self.get_all_clients()
        return [l for l in leads if l["status"] == status]

    def _clean_budget(self, budget):
        if isinstance(budget, (int, float)):
            return int(budget)
        budget_str = str(budget).lower().replace(",", "").replace("₹", "").replace("$", "").strip()
        import re
        match = re.search(r'(\d+)', budget_str)
        if match:
            return int(match.group(1))
        return 0