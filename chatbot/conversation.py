"""
==================================================
TechSoul AI
Conversation Engine
==================================================

Controls the chatbot conversation flow by coordinating memory,
input validation, and AI parsing.
"""

from datetime import datetime
from chatbot.state_machine import ChatState
from chatbot.prompt_engine import PromptEngine
from chatbot.memory import ConversationMemory
from chatbot.validators import Validator


class ConversationEngine:
    """
    Controls the chatbot conversation logic and state transitions.
    """

    def __init__(self):
        """
        Initialize ConversationEngine.
        """
        self.memory = ConversationMemory()
        self.state = ChatState.WELCOME

    # ==========================================
    # RESET CONVERSATION
    # ==========================================

    def reset(self):
        """
        Reset all conversation memory and states.
        """
        self.memory.reset()
        self.state = ChatState.WELCOME
        self.user_id = None

    # ==========================================
    # GET CURRENT STATE
    # ==========================================

    def get_state(self):
        """
        Get the current conversation state.

        Returns
        -------
        ChatState
            Enum representing current conversational state.
        """
        return self.state

    # ==========================================
    # CHECK IF CHAT IS COMPLETED
    # ==========================================

    def is_finished(self):
        """
        Check if the state machine has marked the consultation as completed.

        Returns
        -------
        bool
            True if completed, False otherwise.
        """
        return self.state == ChatState.COMPLETED

    # ==========================================
    # GET CLIENT DATA
    # ==========================================

    def get_client_data(self):
        """
        Retrieve collected client data from memory.

        Returns
        -------
        dict
            All collected fields.
        """
        return self.memory.get_all()

    # ==========================================
    # GET PROMPT FOR CURRENT STATE
    # ==========================================

    def get_prompt(self):
        """
        Get prompt text for current state.

        Returns
        -------
        str
            A prompt question.
        """
        prompts = {
            ChatState.WELCOME: PromptEngine.welcome(),
            ChatState.ASK_NAME: PromptEngine.ask_name(),
            ChatState.ASK_COMPANY: PromptEngine.ask_company(),
            ChatState.ASK_EMAIL: PromptEngine.ask_email(),
            ChatState.ASK_PHONE: PromptEngine.ask_phone(),
            ChatState.ASK_PROJECT: PromptEngine.ask_project(),
            ChatState.ASK_FEATURES: PromptEngine.ask_features(),
            ChatState.ASK_BUDGET: PromptEngine.ask_budget(),
            ChatState.ASK_TIMELINE: PromptEngine.ask_timeline(),
            ChatState.GENERATE_QUOTE: PromptEngine.generating_quote(),
            ChatState.COMPLETED: PromptEngine.completed()
        }
        return prompts[self.state]

    # ==========================================
    # PROCESS USER MESSAGE
    # ==========================================

    def _local_parse_budget(self, text):
        import re
        text = text.lower().replace(",", "")
        text = text.replace("₹", "").replace("$", "")
        match = re.search(r'(\d+(?:\.\d+)?)\s*(k|lakh|lacs|lac|thousand|m|million)?', text)
        if match:
            val = float(match.group(1))
            suffix = match.group(2)
            if suffix in ['k', 'thousand']:
                val *= 1000
            elif suffix in ['lakh', 'lacs', 'lac']:
                val *= 100000
            elif suffix in ['m', 'million']:
                val *= 1000000
            return int(val)
        return None

    def _local_parse_timeline(self, text):
        text = text.lower()
        if "urgent" in text:
            return "Urgent"
        elif "fast" in text or "quick" in text:
            return "Fast"
        elif "normal" in text or "regular" in text or "standard" in text:
            return "Normal"
        for val in ["Normal", "Fast", "Urgent"]:
            if val.lower() in text:
                return val
        return None

    def _local_parse_project(self, text):
        text = text.lower()
        projects = ["Business Website", "E-Commerce", "Mobile App", "CRM", "ERP", "AI Solution"]
        if "ecommerce" in text or "e-commerce" in text or "shop" in text or "store" in text:
            return "E-Commerce"
        for p in projects:
            if p.lower() in text:
                return p
        if "website" in text or "site" in text:
            return "Business Website"
        if "app" in text or "mobile" in text or "android" in text or "ios" in text:
            return "Mobile App"
        if "crm" in text:
            return "CRM"
        if "erp" in text:
            return "ERP"
        if "ai" in text or "chatbot" in text or "bot" in text:
            return "AI Solution"
        return None

    def _local_parse_features(self, text):
        text = text.lower()
        feature_mapping = {
            "login system": "Login",
            "login": "Login",
            "admin panel": "Admin Panel",
            "dashboard": "Dashboard",
            "payment gateway": "Payment Gateway",
            "inventory management": "Inventory",
            "inventory": "Inventory",
            "reports": "Reports",
            "notifications": "Notifications",
            "email notifications": "Notifications",
            "sms notifications": "Notifications",
            "analytics": "Analytics",
            "api integration": "API Integration",
            "ai chatbot": "AI Chatbot",
            "multi language": "Multi Language"
        }
        extracted = []
        for key, val in feature_mapping.items():
            if key in text:
                if val not in extracted:
                    extracted.append(val)
        return extracted if extracted else None

    def _normalize_feature_name(self, name):
        feature_mapping = {
            "login system": "Login",
            "login": "Login",
            "admin panel": "Admin Panel",
            "dashboard": "Dashboard",
            "payment gateway": "Payment Gateway",
            "inventory management": "Inventory",
            "inventory": "Inventory",
            "reports": "Reports",
            "notifications": "Notifications",
            "email notifications": "Notifications",
            "sms notifications": "Notifications",
            "analytics": "Analytics",
            "api integration": "API Integration",
            "ai chatbot": "AI Chatbot",
            "multi language": "Multi Language"
        }
        return feature_mapping.get(name.lower(), name)

    def load_session(self, chat_id):
        """
        Load conversation state and memory from SQLite.
        """
        from backend.services.database import DatabaseService
        import json
        db = DatabaseService()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT state_json, user_id FROM chats WHERE id = ?", (chat_id,))
            row = cursor.fetchone()
            if row:
                self.user_id = row["user_id"]
                if row["state_json"]:
                    try:
                        data = json.loads(row["state_json"])
                        state_val = data.get("state", ChatState.WELCOME.value)
                        self.state = ChatState(state_val)
                        self.memory.client = data.get("client", {})
                    except Exception:
                        self.state = ChatState.WELCOME
                        self.memory.reset()
                else:
                    self.state = ChatState.WELCOME
                    self.memory.reset()
            else:
                self.user_id = None
                self.state = ChatState.WELCOME
                self.memory.reset()

    def get_customer_memory_context(self, user_id):
        """
        Fetch profile, projects, proposals, quotations, and uploaded files for returning customer context.
        """
        if not user_id:
            return None
        from backend.services.database import DatabaseService
        import json
        db = DatabaseService()
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                # Profile
                cursor.execute(
                    "SELECT name, company, email, phone, business_type, country, website, address FROM users WHERE id = ?",
                    (user_id,)
                )
                user_row = cursor.fetchone()
                if not user_row:
                    return None
                
                profile = dict(user_row)
                
                # Projects, Quotations & Proposals
                cursor.execute(
                    """
                    SELECT p.id as project_id, p.name as project_name, p.status, p.budget, p.timeline, p.created_at,
                           q.details_json as quotation_json,
                           pr.executive_summary, pr.goals_json, pr.scope, pr.pdf_file
                    FROM projects p
                    LEFT JOIN quotations q ON q.project_id = p.id
                    LEFT JOIN proposals pr ON pr.project_id = p.id
                    WHERE p.user_id = ?
                    ORDER BY p.id DESC
                    """,
                    (user_id,)
                )
                projects = []
                for row in cursor.fetchall():
                    proj = {
                        "name": row["project_name"],
                        "status": row["status"],
                        "budget": row["budget"],
                        "timeline": row["timeline"],
                        "created_at": row["created_at"]
                    }
                    if row["quotation_json"]:
                        try:
                            proj["quotation"] = json.loads(row["quotation_json"])
                        except:
                            pass
                    if row["goals_json"]:
                        try:
                            proj["goals"] = json.loads(row["goals_json"])
                        except:
                            pass
                    projects.append(proj)
                
                # Files uploaded
                cursor.execute("SELECT filename, created_at FROM files WHERE user_id = ? ORDER BY id DESC", (user_id,))
                files = [{"filename": r["filename"], "uploaded_at": r["created_at"]} for r in cursor.fetchall()]
                
                return {
                    "profile": profile,
                    "past_projects": projects,
                    "uploaded_files": files
                }
        except Exception as e:
            print(f"Error fetching customer memory: {e}")
            return None

    def save_session(self, chat_id):
        """
        Save conversation state and memory to SQLite.
        """
        from backend.services.database import DatabaseService
        import json
        db = DatabaseService()
        data = {
            "state": self.state.value if hasattr(self.state, "value") else str(self.state),
            "client": self.memory.client
        }
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE chats SET state_json = ?, updated_at = ? WHERE id = ?",
                (json.dumps(data), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), chat_id)
            )
            conn.commit()

    def process(self, message):
        """
        Process the user's message using Gemini to extract key client fields,
        formulate a natural sales representative response, and track the status.

        Parameters
        ----------
        message : str
            Input message from client.

        Returns
        -------
        str or dict
            The bot's response message (or dictionary completion payload).
        """
        message = message.strip()

        # ======================================
        # START CONVERSATION / WELCOME
        # ======================================
        if self.state == ChatState.WELCOME:
            self.state = ChatState.ASK_NAME
            welcome_msg = PromptEngine.welcome()
            
            # Seed the message history
            messages = self.memory.client.get("messages", [])
            messages.append({"role": "bot", "content": welcome_msg})
            self.memory.set("messages", messages)
            
            return welcome_msg

        # ======================================
        # NATURAL LANGUAGE ENGINE
        # ======================================
        from backend.services.gemini_service import GeminiService
        gemini = GeminiService()

        client_data = self.memory.get_all().copy()
        history = client_data.get("messages", [])

        # Fetch returning customer memory from database and add to client_data
        if hasattr(self, "user_id") and self.user_id:
            customer_memory = self.get_customer_memory_context(self.user_id)
            if customer_memory:
                client_data["customer_memory"] = customer_memory

        # Call Gemini to parse fields and respond as Alex the sales representative
        try:
            analysis = gemini.analyze_chat(client_data, message, history)
            is_gemini_fallback = not analysis.get("extracted_data") and "Interesting!" in analysis.get("response", "")
        except Exception:
            analysis = {"extracted_data": {}, "response": "", "completed": False}
            is_gemini_fallback = True

        # If Gemini returned fallback or empty, let's extract data locally!
        if is_gemini_fallback or not analysis.get("extracted_data"):
            extracted = {}
            if self.state == ChatState.ASK_BUDGET:
                b_val = self._local_parse_budget(message)
                if b_val:
                    extracted["budget"] = b_val
            elif self.state == ChatState.ASK_TIMELINE:
                t_val = self._local_parse_timeline(message)
                if t_val:
                    extracted["timeline"] = t_val
            elif self.state == ChatState.ASK_PROJECT:
                p_val = self._local_parse_project(message)
                if p_val:
                    extracted["project"] = p_val
            elif self.state == ChatState.ASK_FEATURES:
                f_val = self._local_parse_features(message)
                if f_val:
                    extracted["features"] = f_val
            elif self.state == ChatState.ASK_NAME:
                cleaned_name = message.strip()
                for prefix in ["my name is ", "i am ", "myself "]:
                    if cleaned_name.lower().startswith(prefix):
                        cleaned_name = cleaned_name[len(prefix):]
                if cleaned_name:
                    extracted["name"] = cleaned_name
            elif self.state == ChatState.ASK_COMPANY:
                cleaned_comp = message.strip()
                for prefix in ["my company is ", "it is ", "i work at "]:
                    if cleaned_comp.lower().startswith(prefix):
                        cleaned_comp = cleaned_comp[len(prefix):]
                if cleaned_comp:
                    extracted["company"] = cleaned_comp
            elif self.state == ChatState.ASK_EMAIL:
                for word in message.split():
                    if Validator.validate_email(word):
                        extracted["email"] = word
            elif self.state == ChatState.ASK_PHONE:
                if Validator.validate_phone(message):
                    extracted["phone"] = message
                else:
                    for word in message.split():
                        if Validator.validate_phone(word):
                            extracted["phone"] = word

            analysis["extracted_data"] = extracted

        # Update client memory with parsed details
        extracted = analysis.get("extracted_data", {})
        for key, value in extracted.items():
            if value is not None and value != "" and value != []:
                if key == "features":
                    if self.state == ChatState.ASK_FEATURES and isinstance(value, list):
                        for f in value:
                            normalized_f = self._normalize_feature_name(f)
                            if normalized_f:
                                self.memory.add_feature(normalized_f)
                else:
                    self.memory.set(key, value)

        # Save conversation turn in history
        history.append({"role": "user", "content": message})
        reply = analysis.get("response", "Could you tell me more about your project?")
        
        # Update email/phone if we can extract them using validators
        for word in message.split():
            if Validator.validate_email(word):
                self.memory.set("email", word)
            elif Validator.validate_phone(word):
                self.memory.set("phone", word)

        # Determine next logical ChatState based on missing requirements
        client_all = self.memory.get_all()
        completed = analysis.get("completed", False) or self.memory.is_complete()

        if completed:
            if not client_all.get("email"):
                self.state = ChatState.ASK_EMAIL
                missing_email_reply = "I have your project details. Could you please share your email address so I can send the proposal?"
                history.append({"role": "bot", "content": missing_email_reply})
                self.memory.set("messages", history)
                return missing_email_reply
            elif not client_all.get("phone"):
                self.state = ChatState.ASK_PHONE
                missing_phone_reply = "Great. And your phone number so our sales team can contact you?"
                history.append({"role": "bot", "content": missing_phone_reply})
                self.memory.set("messages", history)
                return missing_phone_reply
            
            self.state = ChatState.COMPLETED
            return {
                "completed": True,
                "client": self.memory.get_all()
            }
        else:
            # Map state progression to guide frontend panel display
            if not client_all.get("name"):
                self.state = ChatState.ASK_NAME
            elif not client_all.get("company"):
                self.state = ChatState.ASK_COMPANY
            elif not client_all.get("project"):
                self.state = ChatState.ASK_PROJECT
            elif not client_all.get("features"):
                self.state = ChatState.ASK_FEATURES
            elif not client_all.get("budget"):
                self.state = ChatState.ASK_BUDGET
            elif not client_all.get("timeline"):
                self.state = ChatState.ASK_TIMELINE
            else:
                self.state = ChatState.GENERATE_QUOTE

            # If Gemini failed/fallback occurred, use our custom reply
            if is_gemini_fallback or not reply or reply.startswith("Interesting! Tell me more about that."):
                if self.state == ChatState.ASK_BUDGET:
                    reply = "What is your estimated budget for this project? (e.g. ₹50k, ₹1.5 Lakhs)"
                elif self.state == ChatState.ASK_TIMELINE:
                    reply = "Great! Choose your preferred timeline:\n\n• Normal\n• Fast\n• Urgent"
                elif self.state == ChatState.ASK_PROJECT:
                    reply = "Which type of project are you looking for?\n\n• Business Website\n• E-Commerce\n• Mobile App\n• CRM\n• ERP\n• AI Solution"
                elif self.state == ChatState.ASK_FEATURES:
                    reply = PromptEngine.ask_features(client_all.get("budget"))
                elif self.state == ChatState.ASK_NAME:
                    reply = "What is your full name?"
                elif self.state == ChatState.ASK_COMPANY:
                    reply = "Great! What is your company name?"
                elif self.state == ChatState.ASK_EMAIL:
                    reply = "I have your project details. Could you please share your email address so I can send the proposal?"
                elif self.state == ChatState.ASK_PHONE:
                    reply = "Great. And your phone number so our sales team can contact you?"
                else:
                    reply = "Thank you! I have all the details. Generating your quotation now..."

            history.append({"role": "bot", "content": reply})
            self.memory.set("messages", history)
            return reply