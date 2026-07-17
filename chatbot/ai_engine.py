"""
==================================================
TechSoul AI
AI Engine
==================================================

Handles quotation generation, proposal compilation, and lead processing.
"""

import os
from backend.services.pricing import PricingService
from backend.services.proposal import ProposalService
from backend.services.crm import CRMService


class AIEngine:
    """
    Coordinates pricing calculation, proposal generation, and lead closing workflows.
    """

    def __init__(self):
        """
        Initialize AIEngine and services.
        """
        self.pricing = PricingService()
        self.proposal = ProposalService()
        self.crm = CRMService()

    # ==================================================
    # GENERATE QUOTATION
    # ==================================================

    def generate_quotation(self, client):
        """
        Compute final price quote based on client metrics.
        """
        quotation = self.pricing.generate_final_quote(
            project=client["project"],
            features=client["features"],
            budget=client["budget"],
            timeline=client["timeline"]
        )
        return quotation

    # ==================================================
    # GENERATE PROPOSAL
    # ==================================================

    def generate_proposal(self, client):
        """
        Assemble customized project proposal document.
        """
        quotation = self.generate_quotation(client)
        proposal = self.proposal.generate(client, quotation)
        return proposal

    # ==================================================
    # COMPLETE SALES PROCESS
    # ==================================================

    def process_client(self, client):
        """
        Execute backend sales closure: quotation pricing, proposal drafting,
        CRM record creation, PDF file compilation, and email delivery.

        Parameters
        ----------
        client : dict
            Client details.

        Returns
        -------
        dict
            Calculated quotation and proposal models.
        """
        quotation = self.generate_quotation(client)
        proposal = self.proposal.generate(client, quotation)

        # Save to CRM Database
        lead = self.crm.save_client(
            client,
            quotation,
            proposal
        )

        # ---------------------------------------------
        # Generate PDF Proposal
        # ---------------------------------------------
        pdf_path = None
        pdf_filename = f"proposal_{lead['lead_id']}.pdf"
        try:
            from backend.services.pdf_generator import PDFGenerator
            from backend.config import PDF_FOLDER
            
            pdf_gen = PDFGenerator()
            pdf_path = os.path.join(PDF_FOLDER, pdf_filename)
            
            # Write document layout
            pdf_gen.generate(proposal, pdf_path)
            
            # Save PDF filename references in CRM lead (SQLite database)
            self.crm.update_proposal_pdf(lead["lead_id"], pdf_filename)
            
        except Exception as e:
            print(f"Error compiling PDF proposal: {e}")

        # ---------------------------------------------
        # Generate Technical Blueprint (PDF and DOCX)
        # ---------------------------------------------
        try:
            from backend.services.blueprint import BlueprintService
            from backend.config import PDF_FOLDER
            
            blueprint_service = BlueprintService()
            blueprint_data = blueprint_service.generate_blueprint_data(client, quotation)
            
            blueprint_pdf_filename = f"blueprint_{lead['lead_id']}.pdf"
            blueprint_pdf_path = os.path.join(PDF_FOLDER, blueprint_pdf_filename)
            blueprint_service.build_pdf(blueprint_data, blueprint_pdf_path, client, quotation)
            
            blueprint_docx_filename = f"blueprint_{lead['lead_id']}.docx"
            blueprint_docx_path = os.path.join(PDF_FOLDER, blueprint_docx_filename)
            blueprint_service.build_docx(blueprint_data, blueprint_docx_path, client, quotation)
            
            print("Successfully compiled PDF and DOCX technical blueprints.")
        except Exception as e:
            print(f"Error compiling technical blueprints: {e}")

        # ---------------------------------------------
        # Automate Email Delivery (Non-blocking fallback)
        # ---------------------------------------------
        receiver_email = client.get("email")
        if receiver_email:
            try:
                from backend.services.email_service import EmailService
                email_svc = EmailService()
                
                subject = f"Software Project Proposal from TechSoul AI - Lead {lead['lead_id']}"
                
                body = f"""Dear {client.get('name', 'Valued Client')},

Thank you for consulting with TechSoul AI! We are excited about the opportunity to partner with you.

We have prepared a customized proposal for your project '{quotation.get('project')}' based on our conversation.

PROJECT ESTIMATES:
- Project Type: {quotation.get('project')}
- Chosen Features: {', '.join(quotation.get('features', []))}
- Delivery Timeline: {quotation.get('timeline')}
- Estimated Project Total: ₹{quotation.get('total'):,} (Includes Base, Selected Features, GST taxes, and maintenance support)

Please find the detailed project proposal document attached as a PDF.

Our project coordinator will contact you shortly to review timelines and answer any questions.

Best Regards,
Alex (Lead Sales Representative)
TechSoul AI Team
info@techsoulai.com
www.techsoulai.com
"""
                email_svc.send(
                    receiver=receiver_email,
                    subject=subject,
                    body=body,
                    attachment=pdf_path
                )
            except Exception as e:
                # Log email errors but do not crash the conversation loop
                print(f"Email Automation Warning: SMTP transmission failed ({e})")

        return {
            "quotation": quotation,
            "proposal": proposal,
            "pdf_file": pdf_filename
        }

    # ==================================================
    # PROJECT RECOMMENDATIONS
    # ==================================================

    def recommend_project(self, budget):
        """
        Suggest project formats based on funding.
        """
        budget_val = self.pricing.parse_budget(budget)
        if budget_val < 50000:
            return ["Business Website"]
        elif budget_val < 150000:
            return ["Business Website", "E-Commerce", "CRM"]
        elif budget_val < 300000:
            return ["CRM", "Mobile App", "AI Solution"]
        return ["ERP", "AI Solution", "Enterprise CRM"]

    # ==================================================
    # FEATURE RECOMMENDATIONS
    # ==================================================

    def recommend_features(self, project):
        """
        Recommend standard initial features.
        """
        return self.pricing.data.get(
            "recommendations",
            {}
        ).get(project, [])