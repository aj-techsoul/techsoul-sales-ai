"""
==================================================
TechSoul AI
Proposal Service
==================================================

Generates a complete business proposal including client details,
AI-written executive summaries, technology stack recommendations,
milestone payments, and support terms.
"""

from backend.config import (
    COMPANY_NAME,
    COMPANY_EMAIL,
    COMPANY_PHONE,
    COMPANY_WEBSITE,
    COMPANY_ADDRESS
)


class ProposalService:
    """
    Generates detailed corporate software development proposals.
    """

    def __init__(self):
        """
        Initialize ProposalService.
        """
        pass

    # ==================================================
    # GENERATE PROPOSAL
    # ==================================================

    def generate(self, client, quotation):
        """
        Create a proposal dictionary combining quotation data and AI proposal content.

        Parameters
        ----------
        client : dict
            Collected client data from conversation.
        quotation : dict
            Pricing calculation details.

        Returns
        -------
        dict
            Populated proposal layout.
        """
        # Call Gemini AI to write custom proposal copy
        from backend.services.gemini_service import GeminiService
        gemini = GeminiService()
        ai_sections = gemini.write_proposal_sections(client, quotation)

        proposal = {
            "company": COMPANY_NAME,
            "title": f"Software Development Proposal for {client.get('company', 'our client')}",
            "client": self.get_client(client),
            "project": {
                "type": quotation["project"],
                "overview": ai_sections.get(
                    "executive_summary", 
                    self.get_project_overview(quotation["project"])
                ),
                "technology": self.get_technology_stack(quotation["project"]),
                "timeline": quotation["timeline"],
                "features": quotation["features"],
                "scope": ai_sections.get(
                    "scope", 
                    "Full scale design, engineering, QA, and deployment of features."
                )
            },
            "goals": ai_sections.get("goals", self.get_default_goals(quotation["project"])),
            "quotation": self.get_quotation_details(quotation),
            "deliverables": self.get_deliverables(),
            "support": self.get_support(),
            "terms": self.get_terms(),
            "next_steps": self.get_next_steps()
        }

        return proposal

    # ==================================================
    # CLIENT
    # ==================================================

    def get_client(self, client):
        """
        Format client details.
        """
        return {
            "name": client.get("name", ""),
            "company": client.get("company", ""),
            "email": client.get("email", ""),
            "phone": client.get("phone", "")
        }

    # ==================================================
    # PROJECT DETAILS
    # ==================================================

    def get_project_details(self, quotation):
        """
        Format project details for backward-compatibility.
        """
        return {
            "type": quotation["project"],
            "overview": self.get_project_overview(quotation["project"]),
            "technology": self.get_technology_stack(quotation["project"]),
            "timeline": quotation["timeline"],
            "features": quotation["features"]
        }

    # ==================================================
    # QUOTATION
    # ==================================================

    def get_quotation_details(self, quotation):
        """
        Format quotation breakdown.
        """
        return {
            "project_price": quotation["project_price"],
            "feature_price": quotation["feature_price"],
            "subtotal": quotation["subtotal"],
            "discount": quotation.get("discount", 0),
            "taxes": quotation.get("taxes", 0),
            "maintenance": quotation.get("maintenance", 0),
            "total": quotation["total"],
            "budget": quotation.get("budget", 0),
            "remaining_budget": quotation.get("remaining_budget", 0),
            "removed_features": quotation.get("removed_features", []),
            "recommended_upgrades": quotation.get("recommended_upgrades", []),
            "payment_schedule": self.get_payment_schedule(quotation["total"])
        }

    # ==================================================
    # PROJECT OVERVIEW
    # ==================================================

    def get_project_overview(self, project):
        """
        Return standard project type summaries.
        """
        overview = {
            "Business Website": "Professional responsive corporate website optimized for SEO.",
            "E-Commerce": "Scalable online shopping platform with secure cart and payment processing.",
            "Mobile App": "Modern native or hybrid mobile application for Android and iOS devices.",
            "CRM": "Customer Relationship Management system designed to manage and optimize leads.",
            "ERP": "Enterprise Resource Planning tool for centralizing business data and processes.",
            "AI Solution": "Intelligent software agent utilizing machine learning models to solve problems."
        }
        return overview.get(project, "Custom software development solution.")

    # ==================================================
    # DEFAULT GOALS
    # ==================================================

    def get_default_goals(self, project):
        """
        Fallback goals.
        """
        return [
            "Establish a modern digital footprint for the brand.",
            "Improve operational efficiencies with automated features.",
            "Provide user-friendly, responsive software interfaces."
        ]

    # ==================================================
    # TECHNOLOGY STACK
    # ==================================================

    def get_technology_stack(self, project):
        """
        Recommend standard tech stacks for various project types.
        """
        stack = {
            "Business Website": ["HTML5/CSS3", "Next.js", "Flask API", "PostgreSQL"],
            "E-Commerce": ["React", "FastAPI", "MongoDB", "Razorpay / Stripe Integration"],
            "Mobile App": ["Flutter", "Node.js", "Firebase Firestore", "Google Cloud Functions"],
            "CRM": ["Next.js", "Spring Boot", "MySQL", "AWS RDS"],
            "ERP": ["Angular", "Laravel", "PostgreSQL", "Docker / Kubernetes"],
            "AI Solution": ["Python", "TensorFlow / PyTorch", "FastAPI", "Vector Database", "AWS SageMaker"]
        }
        return stack.get(project, ["React", "Flask", "MySQL"])

    # ==================================================
    # PAYMENT SCHEDULE
    # ==================================================

    def get_payment_schedule(self, total):
        """
        Format payment milestones.
        """
        return [
            {
                "stage": "Advance Kickoff",
                "percentage": "50%",
                "amount": round(total * 0.50)
            },
            {
                "stage": "Beta / Development Release",
                "percentage": "30%",
                "amount": round(total * 0.30)
            },
            {
                "stage": "Production Launch / Handover",
                "percentage": "20%",
                "amount": round(total * 0.20)
            }
        ]

    # ==================================================
    # DELIVERABLES
    # ==================================================

    def get_deliverables(self):
        """
        Return default list of deliverables.
        """
        return [
            "Complete Clean Source Code Git Repository access",
            "Functional staging and production database setup",
            "Full mobile/desktop responsive design implementation",
            "Secure administrator dashboard panel",
            "External payment and API service integrations",
            "Hosting server setup and domain configuration support",
            "Complete technical system architecture documentation",
            "Post-launch administrator operational training session"
        ]

    # ==================================================
    # SUPPORT
    # ==================================================

    def get_support(self):
        """
        Return support terms.
        """
        return {
            "warranty": "90 Days post-launch guarantee",
            "maintenance": "Comprehensive annual support options",
            "bug_fix": "Complimentary critical bugs fix during warranty",
            "technical_support": "Email, Phone & Slack support"
        }

    # ==================================================
    # TERMS
    # ==================================================

    def get_terms(self):
        """
        Return legal terms.
        """
        return [
            "Proposal quotation remains valid for 30 days from document receipt.",
            "Development begins immediately upon advance invoice payment approval.",
            "Scope variations requested after project commencement are billed separately.",
            "All intellectual property transfers to client upon final milestone payment settlement.",
            "Timelines are subject to user assets receipt dependencies."
        ]

    # ==================================================
    # NEXT STEPS
    # ==================================================

    def get_next_steps(self):
        """
        Return next onboarding steps.
        """
        return [
            "Review and comment on the proposal document details.",
            "Confirm timeline dates alignment with sales managers.",
            "Approve proposal quotation and execute initial payment milestone invoice.",
            "Schedule technical onboarding / discovery alignment kickoff workshop.",
            "Active engineering design and codebase sprint commences."
        ]