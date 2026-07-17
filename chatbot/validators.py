"""
==================================================
TechSoul AI
Input Validators
==================================================

Validates all user inputs.
"""

import re


class Validator:

    # ==========================================
    # NAME
    # ==========================================

    @staticmethod
    def validate_name(name):

        name = name.strip()

        if len(name) < 2:
            return False

        return bool(
            re.fullmatch(
                r"[A-Za-z ]+",
                name
            )
        )

    # ==========================================
    # COMPANY
    # ==========================================

    @staticmethod
    def validate_company(company):

        return len(company.strip()) >= 2

    # ==========================================
    # EMAIL
    # ==========================================

    @staticmethod
    def validate_email(email):

        pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

        return bool(
            re.fullmatch(
                pattern,
                email
            )
        )

    # ==========================================
    # PHONE
    # ==========================================

    @staticmethod
    def validate_phone(phone):
        phone = phone.strip()
        try:
            import phonenumbers
            parsed = phonenumbers.parse(phone, None)
            return phonenumbers.is_valid_number(parsed)
        except Exception:
            # Fallback regex matching: optionally starts with +, followed by 7 to 15 digits
            clean_phone = re.sub(r"[\s\-()]+", "", phone)
            return bool(re.match(r"^\+?\d{7,15}$", clean_phone))

    # ==========================================
    # PROJECT
    # ==========================================

    @staticmethod
    def validate_project(project):

        projects = [

            "Business Website",

            "E-Commerce",

            "Mobile App",

            "CRM",

            "ERP",

            "AI Solution"

        ]

        return project in projects

    # ==========================================
    # FEATURES
    # ==========================================

    @staticmethod
    def validate_features(features):

        available = {

            "Login",

            "Admin Panel",

            "Dashboard",

            "Payment Gateway",

            "Chat System",

            "Notifications",

            "Reports",

            "Analytics",

            "Inventory",

            "API Integration",

            "AI Chatbot",

            "Multi Language"

        }

        if not features:
            return False

        for feature in features:

            if feature not in available:

                return False

        return True

    # ==========================================
    # BUDGET
    # ==========================================

    @staticmethod
    def validate_budget(budget):

        budget = budget.replace(",", "").replace("₹", "").strip()

        return budget.isdigit()

    # ==========================================
    # TIMELINE
    # ==========================================

    @staticmethod
    def validate_timeline(timeline):

        return timeline in [

            "Normal",

            "Fast",

            "Urgent"

        ]