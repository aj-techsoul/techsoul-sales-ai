"""
==================================================
TechSoul AI
Conversation State Machine
==================================================

Defines all chatbot conversation states.
"""

from enum import Enum


class ChatState(Enum):
    """
    Chatbot Conversation States
    """

    # ==========================================
    # INITIAL
    # ==========================================

    WELCOME = "WELCOME"

    # ==========================================
    # CLIENT DETAILS
    # ==========================================

    ASK_NAME = "ASK_NAME"

    ASK_COMPANY = "ASK_COMPANY"

    ASK_EMAIL = "ASK_EMAIL"

    ASK_PHONE = "ASK_PHONE"

    # ==========================================
    # PROJECT DETAILS
    # ==========================================

    ASK_PROJECT = "ASK_PROJECT"

    ASK_FEATURES = "ASK_FEATURES"

    ASK_BUDGET = "ASK_BUDGET"

    ASK_TIMELINE = "ASK_TIMELINE"

    # ==========================================
    # QUOTATION
    # ==========================================

    GENERATE_QUOTE = "GENERATE_QUOTE"

    SHOW_QUOTE = "SHOW_QUOTE"

    # ==========================================
    # PROPOSAL
    # ==========================================

    GENERATE_PROPOSAL = "GENERATE_PROPOSAL"

    SEND_PROPOSAL = "SEND_PROPOSAL"

    # ==========================================
    # UPSELL
    # ==========================================

    UPSELL = "UPSELL"

    # ==========================================
    # FINISH
    # ==========================================

    COMPLETED = "COMPLETED"