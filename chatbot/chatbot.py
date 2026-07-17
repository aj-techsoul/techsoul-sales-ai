"""
==================================================
TechSoul AI
Main Chatbot Controller
==================================================

Coordinates the Conversation Engine and the AI Engine to
drive conversational consultations.
"""

from chatbot.conversation import ConversationEngine
from chatbot.ai_engine import AIEngine
from chatbot.prompt_engine import PromptEngine


class TechSoulChatbot:
    """
    Coordinates chat progression, quotation generation, and proposals.
    """

    def __init__(self):
        """
        Initialize chatbot controller with engine instances.
        """
        self.conversation = ConversationEngine()
        self.ai = AIEngine()

    # ==================================================
    # START CHAT
    # ==================================================

    def start(self, welcome_back_info=None):
        """
        Start a new conversation session.

        Parameters
        ----------
        welcome_back_info : dict, optional
            Contains profile data and previous project name to greet returning users.

        Returns
        -------
        dict
            Welcome state configuration.
        """
        self.conversation.reset()
        
        if welcome_back_info:
            self.conversation.user_id = welcome_back_info.get("user_id")
            profile = welcome_back_info.get("profile", {})
            for k, v in profile.items():
                if v:
                    self.conversation.memory.set(k, v)
            
            name = profile.get("name", "there")
            prev_proj_name = welcome_back_info.get("prev_project")
            
            if prev_proj_name:
                first_message = (
                    f"Welcome back, {name}.\n\n"
                    f"It's great to see you again.\n\n"
                    f"I found your previous discussion regarding your **{prev_proj_name}**.\n\n"
                    f"Would you like to continue that project or start discussing a new idea?"
                )
            else:
                first_message = (
                    f"Welcome back, {name}! It's great to see you again.\n\n"
                    f"I have loaded your profile. What kind of new project are we building for your business today?"
                )

            # Progress state past welcome since we already know the client details
            from chatbot.state_machine import ChatState
            if not profile.get("name"):
                self.conversation.state = ChatState.ASK_NAME
            elif not profile.get("company"):
                self.conversation.state = ChatState.ASK_COMPANY
            else:
                self.conversation.state = ChatState.ASK_PROJECT

            # Seed the message history with the welcome back message
            messages = self.conversation.memory.client.get("messages", [])
            messages.append({"role": "bot", "content": first_message})
            self.conversation.memory.set("messages", messages)
        else:
            first_message = self.conversation.process("")

        # Extract name from chat state Enum representation
        state_str = self.get_state_string()

        return {
            "reply": first_message,
            "completed": False,
            "quotation": None,
            "proposal": None,
            "state": state_str
        }

    # ==================================================
    # PROCESS USER MESSAGE
    # ==================================================

    def reply(self, message):
        """
        Process incoming message, progress states, and run closing services.

        Parameters
        ----------
        message : str
            User input string.

        Returns
        -------
        dict
            Conversation status and summary/proposal when completed.
        """
        response = self.conversation.process(message)
        state_str = self.get_state_string()

        # ----------------------------------------------
        # Conversation still running
        # ----------------------------------------------
        if not self.conversation.is_finished():
            return {
                "reply": response,
                "completed": False,
                "quotation": None,
                "proposal": None,
                "state": state_str
            }

        # ----------------------------------------------
        # Conversation completed
        # ----------------------------------------------
        client = self.conversation.get_client_data()
        result = self.ai.process_client(client)
        quotation = result["quotation"]
        proposal = result["proposal"]
        pdf_file = result.get("pdf_file", "")

        summary = PromptEngine.final_summary(
            client,
            quotation
        )

        return {
            "reply": summary,
            "completed": True,
            "quotation": quotation,
            "proposal": proposal,
            "pdf_file": pdf_file,
            "state": "COMPLETED"
        }

    # ==================================================
    # GET STATE STRING HELPER
    # ==================================================

    def get_state_string(self):
        """
        Extract simplified state string.
        """
        state = self.get_state()
        if hasattr(state, "value"):
            return state.value
        return str(state)

    # ==================================================
    # BUILD FINAL SUMMARY
    # ==================================================

    def build_final_summary(self, client, quotation):
        """
        Build chatbot final summary string (retained for backward compatibility).
        """
        return PromptEngine.final_summary(client, quotation)

    # ==================================================
    # RESET CHAT
    # ==================================================

    def reset(self):
        """
        Reset engines.
        """
        self.conversation.reset()

    # ==================================================
    # GET CLIENT
    # ==================================================

    def get_client(self):
        """
        Retrieve memory client data.
        """
        return self.conversation.get_client_data()

    # ==================================================
    # GET STATE
    # ==================================================

    def get_state(self):
        """
        Retrieve conversational ChatState.
        """
        return self.conversation.get_state()