"""
==================================================
TechSoul AI
Conversation Memory
==================================================

Stores all client information collected during
the conversation.
"""


class ConversationMemory:
    """
    Stores conversation data.
    """

    def __init__(self):

        self.reset()

    # ==========================================
    # RESET MEMORY
    # ==========================================

    def reset(self):
        """
        Reset all conversation data.
        """

        self.client = {

            # Client Information
            "name": "",
            "company": "",
            "business_type": "",
            "industry": "",
            "email": "",
            "phone": "",
            "country": "",

            # Project Information
            "project": "",
            "features": [],
            "budget": "",
            "timeline": "",

            # Message History
            "messages": [],

            # Generated Data
            "quotation": {},
            "proposal": {}

        }

    # ==========================================
    # SET VALUE
    # ==========================================

    def set(self, key, value):
        """
        Store a value in memory.
        """

        if key in self.client:

            self.client[key] = value

    # ==========================================
    # GET VALUE
    # ==========================================

    def get(self, key):
        """
        Retrieve a value from memory.
        """

        return self.client.get(key)

    # ==========================================
    # ADD FEATURE
    # ==========================================

    def add_feature(self, feature):
        """
        Add a project feature.
        """

        if feature not in self.client["features"]:

            self.client["features"].append(feature)

    # ==========================================
    # REMOVE FEATURE
    # ==========================================

    def remove_feature(self, feature):
        """
        Remove a project feature.
        """

        if feature in self.client["features"]:

            self.client["features"].remove(feature)

    # ==========================================
    # CLEAR FEATURES
    # ==========================================

    def clear_features(self):
        """
        Remove all selected features.
        """

        self.client["features"] = []

    # ==========================================
    # GET COMPLETE DATA
    # ==========================================

    def get_all(self):
        """
        Return all conversation data.
        """

        return self.client

    # ==========================================
    # UPDATE MULTIPLE VALUES
    # ==========================================

    def update(self, data):
        """
        Update multiple values at once.
        """

        for key, value in data.items():

            if key in self.client:

                self.client[key] = value

    # ==========================================
    # CHECK COMPLETION
    # ==========================================

    def is_complete(self):
        """
        Check whether all required fields exist.
        """

        required_fields = [

            "name",
            "company",
            "project",
            "budget",
            "timeline",
            "features"

        ]

        for field in required_fields:

            if not self.client[field]:

                return False

        return True