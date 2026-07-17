"""
==================================================
TechSoul AI
Email Service
==================================================

Sends quotation and proposal emails.
"""

import os
import smtplib

from email.message import EmailMessage
from backend.config import (
    EMAIL_HOST,
    EMAIL_PORT,
    EMAIL_ADDRESS,
    EMAIL_PASSWORD
)


class EmailService:
    """
    Email Service
    """

    def __init__(self):

        self.sender = os.getenv(
            "TECHSOUL_EMAIL",
            "yourcompany@gmail.com"
        )

        self.password = os.getenv(
            "TECHSOUL_PASSWORD",
            "your-app-password"
        )

    # ==========================================
    # SEND EMAIL
    # ==========================================

    def send(

        self,

        receiver,

        subject,

        body,

        attachment=None

    ):

        message = EmailMessage()

        message["From"] = self.sender

        message["To"] = receiver

        message["Subject"] = subject

        message.set_content(body)

        # -----------------------------
        # Attach PDF
        # -----------------------------

        if attachment and os.path.exists(attachment):

            with open(

                attachment,

                "rb"

            ) as file:

                message.add_attachment(

                    file.read(),

                    maintype="application",

                    subtype="pdf",

                    filename=os.path.basename(
                        attachment
                    )

                )

        # -----------------------------
        # Gmail SMTP
        # -----------------------------

        with smtplib.SMTP(

            "smtp.gmail.com",

            587

        ) as smtp:

            smtp.starttls()

            smtp.login(

                self.sender,

                self.password

            )

            smtp.send_message(message)

        return True