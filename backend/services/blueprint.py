"""
==================================================
TechSoul AI
Blueprint Service
==================================================

Generates a complete technical project blueprint from client constraints
including architecture, stack choices, user roles, screen flows, database models,
and REST endpoints in PDF and Word formats.
"""

import os
import json
import re
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class BlueprintService:
    """
    Service to compile dynamic technical specifications and blueprints.
    """

    def __init__(self):
        """
        Initialize BlueprintService.
        """
        self.styles = getSampleStyleSheet()

    def generate_blueprint_data(self, client_data, quotation):
        """
        Query Gemini to generate custom architectural and layout descriptions.
        """
        from backend.services.gemini_service import GeminiService
        gemini = GeminiService()

        prompt = f"""
        You are a Principal Software Architect at TechSoul AI.
        Generate a detailed system design blueprint for the following software project:
        Client Company: {client_data.get('company', 'our client')}
        Project Type: {client_data.get('project', 'Software Solution')}
        Budget Total: ₹{quotation.get('total', 0):,}
        Timeline Scheme: {client_data.get('timeline', 'Normal')}
        Selected Features: {', '.join(client_data.get('features', []))}

        Produce comprehensive, high-value, professional paragraphs for the following parts:
        1. Executive Summary: The business purpose of the project.
        2. Recommended System Architecture: Explain the design pattern (e.g. MVC, Layered Architecture, Microservices, Serverless) and why.
        3. Product Tech Stack: Provide details of each layer (Frontend, Backend, Database, Cloud hosting, APIs).
        4. Database Design: Specify a database model including key tables, column names, types, and primary/foreign key relationships.
        5. User Roles Matrix: Outline permissions for Administrator, User, and Guest.
        6. App Screen Flow: List the key UI screens and what actions users take on them.
        7. REST API Endpoints: State at least 5 REST API routes (HTTP Method, URL, request parameters, response).
        8. Security Implementation: Detail security layers (e.g. password hashing, secure cookies, CORS, SSL, JWT).
        9. Deployment Infrastructure: CI/CD setup, cloud hosting providers (e.g. AWS, Heroku), and runtime environment.
        10. Quality Assurance & Maintenance: Strategy for unit testing, integration tests, and compliments warranty.
        11. Future Expansion Roadmap: Recommending subsequent upgrade phases (e.g. adding AI search, analytics, scale redundancy).

        Return your response ONLY as a valid raw JSON object matching this structure (do not wrap in markdown ```json blocks):
        {{
          "executive_summary": "...",
          "architecture": "...",
          "tech_stack": "...",
          "database_design": "...",
          "user_roles": "...",
          "screen_list": "...",
          "api_list": "...",
          "security": "...",
          "deployment": "...",
          "maintenance_testing": "...",
          "future_expansion": "..."
        }}
        """
        try:
            res = gemini.generate(prompt)
            if res.startswith("```"):
                res = re.sub(r"^```(?:json)?\n", "", res)
                res = re.sub(r"\n```$", "", res)
            return json.loads(res.strip())
        except Exception as e:
            print(f"Error generating AI blueprint details: {e}")
            # Robust fallback text
            return {
                "executive_summary": f"Technical blueprint outlining the software architecture and system components for the '{client_data.get('project')}' solution tailored for {client_data.get('company', 'our client')}.",
                "architecture": "Layered MVC Architecture. Front-end client communicates with a secure server-side API Gateway that interacts with internal services and a central transaction database.",
                "tech_stack": "Frontend: React.js (SaaS UI template), Backend: Python Flask / Node.js, Database: PostgreSQL / SQLite, Cloud: Docker containerization, AWS Hosting support.",
                "database_design": "Users Table (id, email, password_hash, company, created_at)\nProjects Table (id, user_id, name, budget, status, created_at)\nQuotations Table (id, project_id, details_json, created_at)\nProposals Table (id, project_id, scope, created_at)",
                "user_roles": "Administrator: Full dashboard control, CRUD capabilities on users/leads, analytics visibility.\nClient: Settings updates, file uploads access, download quotation & proposals.\nGuest: Basic consultation chat session operations.",
                "screen_list": "1. Authentication (Login & Signup)\n2. Customer Portal Dashboard (Leads, Roadmap, Files list)\n3. Consultation Screen (Chat interface, cards selectors)\n4. Admin CRM Dashboard (Leads tracking table, statistics grid)",
                "api_list": "1. GET /api/start - Initiate chat session\n2. POST /api/chat - Submit message/card\n3. POST /api/upload - Upload requirement documents\n4. GET /api/files - Fetch user documents\n5. GET /api/dashboard/summary - Load stats & user data",
                "security": "PBKDF2 Password hashing algorithm, secure HTTP-only sessions, CSRF token validation, SQL injection prevention through parameterized queries, XSS sanitization.",
                "deployment": "Containerization using Docker, Automated pipeline using GitHub Actions, deployment onto AWS EC2 instance with SSL encryption via Nginx reverse proxy.",
                "maintenance_testing": "Unit testing using Pytest, manual UI verification, compliance debugging support under complimentary 90-day post-launch warranty.",
                "future_expansion": "Phase 2 scale upgrades including PostgreSQL replication, Redis query caching layer, and integration of specialized AI chatbot agents."
            }

    def build_pdf(self, blueprint_data, filename, client_data, quotation):
        """
        Write PDF format project blueprint using ReportLab.
        """
        doc = SimpleDocTemplate(filename, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
        story = []

        title_style = ParagraphStyle(
            "BlueprintTitle",
            parent=self.styles["Heading1"],
            fontSize=26,
            leading=32,
            textColor=colors.HexColor("#1e3a8a"),
            alignment=1, # Center
            spaceAfter=15
        )

        h1_style = ParagraphStyle(
            "BlueprintH1",
            parent=self.styles["Heading2"],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#1e3a8a"),
            spaceBefore=14,
            spaceAfter=8,
            keepWithNext=True
        )

        body_style = ParagraphStyle(
            "BlueprintBody",
            parent=self.styles["BodyText"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#334155"),
            spaceAfter=6
        )

        # Title / Cover info
        story.append(Paragraph("PROJECT TECHNICAL SYSTEM BLUEPRINT", title_style))
        story.append(Spacer(1, 10))

        metadata = [
            ["Prepared For:", client_data.get("company", "Valued Client")],
            ["Project Focus:", quotation.get("project", "Custom Software")],
            ["Development Stack:", "Recommended Architect Choice"],
            ["Timeline Scheme:", client_data.get("timeline", "Normal")],
            ["Total Scope Cost:", f"₹{quotation.get('total', 0):,}"],
            ["Generated On:", datetime.now().strftime("%Y-%m-%d")]
        ]
        
        t = Table(metadata, colWidths=[150, 350])
        t.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#1e3a8a")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ]))
        story.append(t)
        story.append(Spacer(1, 20))
        story.append(PageBreak())

        # Content sections
        sections = [
            ("1. Executive & Business Summary", "executive_summary"),
            ("2. Recommended System Architecture", "architecture"),
            ("3. Product Tech Stack Details", "tech_stack"),
            ("4. Database Schema Design", "database_design"),
            ("5. User Roles & Permission Matrix", "user_roles"),
            ("6. Screen Interface Flow", "screen_list"),
            ("7. REST API Integration Endpoints", "api_list"),
            ("8. Security & Encryption Standards", "security"),
            ("9. Deployment Pipeline & Infrastructure", "deployment"),
            ("10. Maintenance & Quality Assurance", "maintenance_testing"),
            ("11. Future Expansion Roadmap", "future_expansion")
        ]

        for heading, key in sections:
            story.append(Paragraph(heading, h1_style))
            content = blueprint_data.get(key, "-").replace("\n", "<br/>")
            story.append(Paragraph(content, body_style))
            story.append(Spacer(1, 10))

        doc.build(story)
        return filename

    def build_docx(self, blueprint_data, filename, client_data, quotation):
        """
        Write DOCX format project blueprint.
        """
        try:
            import docx
            doc = docx.Document()
            doc.add_heading("PROJECT TECHNICAL SYSTEM BLUEPRINT", level=0)

            doc.add_paragraph(f"Prepared For: {client_data.get('company', 'Valued Client')}")
            doc.add_paragraph(f"Project Focus: {quotation.get('project', 'Custom Software')}")
            doc.add_paragraph(f"Timeline Scheme: {client_data.get('timeline', 'Normal')}")
            doc.add_paragraph(f"Total Scope Cost: ₹{quotation.get('total', 0):,}")
            doc.add_paragraph(f"Generated On: {datetime.now().strftime('%Y-%m-%d')}\n")

            sections = [
                ("1. Executive & Business Summary", "executive_summary"),
                ("2. Recommended System Architecture", "architecture"),
                ("3. Product Tech Stack Details", "tech_stack"),
                ("4. Database Schema Design", "database_design"),
                ("5. User Roles & Permission Matrix", "user_roles"),
                ("6. Screen Interface Flow", "screen_list"),
                ("7. REST API Integration Endpoints", "api_list"),
                ("8. Security & Encryption Standards", "security"),
                ("9. Deployment Pipeline & Infrastructure", "deployment"),
                ("10. Maintenance & Quality Assurance", "maintenance_testing"),
                ("11. Future Expansion Roadmap", "future_expansion")
            ]

            for heading, key in sections:
                doc.add_heading(heading, level=1)
                doc.add_paragraph(blueprint_data.get(key, "-"))

            doc.save(filename)
        except ImportError:
            # Safe text fallback file representing DOCX content
            with open(filename, "w", encoding="utf-8") as f:
                f.write("PROJECT TECHNICAL SYSTEM BLUEPRINT\n")
                f.write("==================================\n\n")
                f.write(f"Prepared For: {client_data.get('company', 'Valued Client')}\n")
                f.write(f"Project Focus: {quotation.get('project', 'Custom Software')}\n")
                f.write(f"Timeline Scheme: {client_data.get('timeline', 'Normal')}\n")
                f.write(f"Total Scope Cost: ₹{quotation.get('total', 0):,}\n")
                f.write(f"Generated On: {datetime.now().strftime('%Y-%m-%d')}\n\n")

                sections = [
                    ("1. Executive & Business Summary", "executive_summary"),
                    ("2. Recommended System Architecture", "architecture"),
                    ("3. Product Tech Stack Details", "tech_stack"),
                    ("4. Database Schema Design", "database_design"),
                    ("5. User Roles & Permission Matrix", "user_roles"),
                    ("6. Screen Interface Flow", "screen_list"),
                    ("7. REST API Integration Endpoints", "api_list"),
                    ("8. Security & Encryption Standards", "security"),
                    ("9. Deployment Pipeline & Infrastructure", "deployment"),
                    ("10. Maintenance & Quality Assurance", "maintenance_testing"),
                    ("11. Future Expansion Roadmap", "future_expansion")
                ]
                for heading, key in sections:
                    f.write(f"\n{heading}\n")
                    f.write("-" * len(heading) + "\n")
                    f.write(blueprint_data.get(key, "-") + "\n")
        return filename
