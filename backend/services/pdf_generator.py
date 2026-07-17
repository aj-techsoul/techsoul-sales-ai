"""
==================================================
TechSoul AI
PDF Proposal Generator
==================================================

Generates a professional PDF proposal document with
branding, metadata, formatting, and pricing tables.
"""

import os
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib import colors
from backend.config import PDF_FOLDER


class PDFGenerator:
    """
    Generates structured proposal PDFs using ReportLab.
    """

    def __init__(self):
        """
        Initialize PDFGenerator with standard styles.
        """
        self.styles = getSampleStyleSheet()

    # ==================================================
    # CREATE PDF
    # ==================================================

    def generate(self, proposal, filename):
        """
        Generate and save a proposal PDF.

        Parameters
        ----------
        proposal : dict
            The complete proposal dictionary.
        filename : str
            Full path to the output PDF file.

        Returns
        -------
        str
            The path of the generated file.
        """
        document = SimpleDocTemplate(filename)
        elements = []

        elements.extend(self.build_header(proposal))
        elements.extend(self.build_client(proposal))
        elements.extend(self.build_project(proposal))
        elements.extend(self.build_quotation(proposal))
        elements.extend(self.build_upgrades(proposal))
        elements.extend(self.build_deliverables(proposal))
        elements.extend(self.build_support(proposal))
        elements.extend(self.build_terms(proposal))
        elements.extend(self.build_footer())

        document.build(elements)
        return filename

    # ==================================================
    # HEADER
    # ==================================================

    def build_header(self, proposal):
        """
        Build corporate header elements.
        """
        story = []
        title = Paragraph(
            "<b><font size=24 color='#1e3a8a'>TechSoul AI</font></b>",
            self.styles["Title"]
        )
        subtitle = Paragraph(
            f"<b>{proposal['title']}</b>",
            self.styles["Heading2"]
        )
        story.append(title)
        story.append(subtitle)
        story.append(Spacer(1, 20))
        return story

    # ==================================================
    # CLIENT
    # ==================================================

    def build_client(self, proposal):
        """
        Build client information section.
        """
        story = []
        client = proposal["client"]
        
        story.append(Paragraph("<b>Client Information</b>", self.styles["Heading2"]))
        story.append(Paragraph(f"<b>Name :</b> {client.get('name', '-')}", self.styles["BodyText"]))
        story.append(Paragraph(f"<b>Company :</b> {client.get('company', '-')}", self.styles["BodyText"]))
        story.append(Paragraph(f"<b>Email :</b> {client.get('email', '-')}", self.styles["BodyText"]))
        story.append(Paragraph(f"<b>Phone :</b> {client.get('phone', '-')}", self.styles["BodyText"]))
        story.append(Spacer(1, 20))
        return story

    # ==================================================
    # PROJECT
    # ==================================================

    def build_project(self, proposal):
        """
        Build project scope and overview section.
        """
        project = proposal["project"]
        story = []

        story.append(Paragraph("<b>Project Details</b>", self.styles["Heading2"]))
        story.append(Paragraph(f"<b>Project Type :</b> {project.get('type', '-')}", self.styles["BodyText"]))
        story.append(Paragraph(f"<b>Expected Timeline :</b> {project.get('timeline', '-')}", self.styles["BodyText"]))
        story.append(Paragraph(f"<b>Overview :</b> {project.get('overview', '-')}", self.styles["BodyText"]))
        
        if project.get("features"):
            features_list = ", ".join(project["features"])
            story.append(Paragraph(f"<b>Key Features :</b> {features_list}", self.styles["BodyText"]))

        story.append(Spacer(1, 20))
        return story

    # ==================================================
    # QUOTATION
    # ==================================================

    def build_quotation(self, proposal):
        """
        Build quotation breakdown table.
        """
        quote = proposal["quotation"]
        story = []

        story.append(Paragraph("<b>Cost Breakdown</b>", self.styles["Heading2"]))

        data = [["Item", "Amount"]]
        
        breakdown = quote.get("cost_breakdown", [])
        if breakdown:
            for b in breakdown:
                data.append([b["item"], f"₹ {b['amount']:,}"])
            data.append(["Grand Total", f"₹ {quote.get('total', 0):,}"])
        else:
            # Fallback to old format if breakdown is missing
            data.extend([
                ["Project Base Price", f"₹ {quote.get('project_price', 0):,}"],
                ["Selected Features Cost", f"₹ {quote.get('feature_price', 0):,}"],
                ["Timeline Multiplier", f"{quote.get('multiplier', 1.0)}x"],
                ["Discounts / Scope Adjustments", f"- ₹ {quote.get('discount', 0):,}"],
                ["Taxes (18% GST)", f"₹ {quote.get('taxes', 0):,}"],
                ["Annual Maintenance (10%)", f"₹ {quote.get('maintenance', 0):,}"],
                ["Final Estimated Total", f"₹ {quote.get('total', 0):,}"]
            ])

        table = Table(data, colWidths=[280, 120])
        t_style = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#cbd5e1")),
            ("TEXTCOLOR", (0, -1), (-1, -1), colors.black),
        ]
        
        # Alternating background colors
        for i in range(1, len(data) - 1):
            if i % 2 == 0:
                t_style.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#f8fafc")))
        table.setStyle(TableStyle(t_style))

        story.append(table)
        story.append(Spacer(1, 20))
        return story

    # ==================================================
    # UPGRADES
    # ==================================================

    def build_upgrades(self, proposal):
        """
        Build list of recommended upsell upgrades.
        """
        story = []
        upgrades = proposal["quotation"].get("recommended_upgrades", [])
        if not upgrades:
            return story

        story.append(Paragraph("<b>Recommended Upgrades</b>", self.styles["Heading2"]))
        for item in upgrades:
            story.append(Paragraph(f"• {item['feature']} - ₹ {item['price']:,}", self.styles["BodyText"]))

        story.append(Spacer(1, 20))
        return story

    # ==================================================
    # DELIVERABLES
    # ==================================================

    def build_deliverables(self, proposal):
        """
        Build deliverables bullet points.
        """
        story = []
        story.append(Paragraph("<b>Project Deliverables</b>", self.styles["Heading2"]))
        
        for item in proposal.get("deliverables", []):
            story.append(Paragraph(f"• {item}", self.styles["BodyText"]))

        story.append(Spacer(1, 20))
        return story

    # ==================================================
    # SUPPORT
    # ==================================================

    def build_support(self, proposal):
        """
        Build support terms.
        """
        support = proposal.get("support", {})
        story = []

        story.append(Paragraph("<b>Support & Warranty</b>", self.styles["Heading2"]))
        story.append(Paragraph(f"<b>Warranty :</b> {support.get('warranty', '30 Days')}", self.styles["BodyText"]))
        story.append(Paragraph(f"<b>Maintenance :</b> {support.get('maintenance', 'Available')}", self.styles["BodyText"]))
        story.append(Paragraph(f"<b>Bug Fix Period :</b> {support.get('bug_fix', 'Included')}", self.styles["BodyText"]))
        story.append(Spacer(1, 20))
        return story

    # ==================================================
    # TERMS
    # ==================================================

    def build_terms(self, proposal):
        """
        Build legal and terms conditions.
        """
        story = []
        story.append(Paragraph("<b>Terms & Conditions</b>", self.styles["Heading2"]))
        
        for term in proposal.get("terms", []):
            story.append(Paragraph(f"• {term}", self.styles["BodyText"]))

        story.append(Spacer(1, 20))
        return story

    # ==================================================
    # FOOTER
    # ==================================================

    def build_footer(self):
        """
        Build closing corporate footer.
        """
        story = []
        story.append(Paragraph("<b>Thank You!</b>", self.styles["Heading2"]))
        story.append(Paragraph("Thank you for choosing TechSoul AI as your digital development partner.", self.styles["BodyText"]))
        story.append(Spacer(1, 20))
        story.append(Paragraph("Authorized Signature", self.styles["BodyText"]))
        story.append(Paragraph("__________________________", self.styles["BodyText"]))
        return story