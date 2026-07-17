"""
==================================================
TechSoul AI
Prompt Engine
==================================================

Contains all chatbot prompts and messages.
"""


class PromptEngine:
    """
    Chatbot Prompt Manager
    """

    # ==========================================
    # WELCOME
    # ==========================================

    @staticmethod
    def welcome():
        return (
            "👋 Welcome to TechSoul AI!\n\n"
            "I'm your AI Business Consultant.\n"
            "I'll help you estimate your project cost and generate a proposal.\n\n"
            "Let's get started.\n\n"
            "What is your name?"
        )

    # ==========================================
    # CLIENT DETAILS
    # ==========================================

    @staticmethod
    def ask_name():
        return "Please enter your full name."

    @staticmethod
    def ask_company():
        return "Great! What is your company name?"

    @staticmethod
    def ask_email():
        return "Please enter your email address."

    @staticmethod
    def ask_phone():
        return "Please enter your phone number."

    # ==========================================
    # PROJECT DETAILS
    # ==========================================

    @staticmethod
    def ask_project():
        return (
            "Which type of project are you looking for?\n\n"
            "• Business Website\n"
            "• E-Commerce\n"
            "• Mobile App\n"
            "• CRM\n"
            "• ERP\n"
            "• AI Solution"
        )

    @staticmethod
    def ask_features(budget=0):
        budget_val = 0
        if budget:
            try:
                from backend.services.pricing import PricingService
                budget_val = PricingService().parse_budget(budget)
            except:
                pass
        
        if budget_val > 0:
            if budget_val < 50000:
                rec = "Basic MVP (e.g. Login System, Dashboard)"
                pkg = "MVP / Core"
            elif budget_val <= 200000:
                rec = "Standard Package (e.g. Login System, Dashboard, Admin Panel, Reports)"
                pkg = "Standard"
            else:
                rec = "Premium Package (e.g. Login System, Dashboard, Admin Panel, Payment Gateway, Analytics, AI Chatbot)"
                pkg = "Premium"
            
            return (
                f"Based on your budget of ₹{budget_val:,}, we recommend selecting our {pkg} features: {rec}.\n\n"
                "Please select the features you would like to include from the panel."
            )
        
        return (
            "Select the features you need.\n"
            "You can choose multiple features."
        )

    @staticmethod
    def ask_budget():
        return "What is your estimated budget?"

    @staticmethod
    def ask_timeline():
        return (
            "Choose your preferred timeline.\n\n"
            "• Normal\n"
            "• Fast\n"
            "• Urgent"
        )

    # ==========================================
    # QUOTATION
    # ==========================================

    @staticmethod
    def generating_quote():
        return "Calculating your quotation..."

    @staticmethod
    def quote_ready():
        return "Your quotation is ready."

    # ==========================================
    # PROPOSAL
    # ==========================================

    @staticmethod
    def generating_proposal():
        return "Generating your project proposal..."

    @staticmethod
    def proposal_ready():
        return "Your proposal has been generated successfully."

    # ==========================================
    # COMPLETION
    # ==========================================

    @staticmethod
    def completed():
        return (
            "Thank you for choosing TechSoul AI.\n"
            "Our team will contact you soon."
        )

    # ==========================================
    # ERRORS
    # ==========================================

    @staticmethod
    def invalid_name():
        return "Please enter a valid name."

    @staticmethod
    def invalid_company():
        return "Please enter a valid company name."

    @staticmethod
    def invalid_email():
        return "Please enter a valid email address."

    @staticmethod
    def invalid_phone():
        return "Please enter a valid phone number."

    @staticmethod
    def invalid_project():
        return "Please select a valid project."

    @staticmethod
    def invalid_budget():
        return "Please enter a valid budget."

    @staticmethod
    def invalid_timeline():
        return "Please choose Normal, Fast or Urgent."

    @staticmethod
    def invalid_input():
        return "Sorry, I didn't understand that. Please try again."

    # ==========================================
    # CONFIRMATION
    # ==========================================

    @staticmethod
    def saved():
        return "Information saved successfully."

    @staticmethod
    def thank_you():
        return "Thank you!"
    @staticmethod
    def final_summary(client, quotation):
        """
        Build the final chatbot business consultant response.
        """
        try:
            from backend.services.pricing import PricingService
            pricing = PricingService()
            project = client.get("project", "E-Commerce")
            budget = client.get("budget", 50000)
            timeline = client.get("timeline", "Normal")
            sim = pricing.simulate_budget(project, budget, timeline)
        except Exception:
            # Fallback simple summary if simulator fails
            return (
                f"🎉 Thank you, {client['name']}!\n\n"
                f"Your project proposal has been generated.\n"
                f"Project Type: {quotation['project']}\n"
                f"Total Price: ₹{quotation['total']:,}\n"
                f"You can download the full PDF proposal from your dashboard."
            )

        lines = []

        lines.append(f"🎉 **Thank you, {client['name']}!**")
        lines.append("")
        lines.append("I have completed a thorough consultative cost and scope analysis for your business solution.")
        lines.append("")
        
        lines.append("### 1. 📋 BUDGET SUMMARY")
        lines.append(f"- **Your Budget**: ₹{sim['budget']:,}")
        lines.append(f"- **Est. MVP Launch Cost**: ₹{sim['options']['option1']['price']:,}")
        lines.append(f"- **Recommended Standard Cost**: ₹{sim['options']['option2']['price']:,}")
        lines.append(f"- **Delivery Timeline**: {sim['timeline']}")
        lines.append("")

        lines.append("### 2. 🟢 FEATURES INCLUDED")
        if sim['features_included']:
            for f in sim['features_included']:
                lines.append(f"  ✔ {f}")
        else:
            lines.append("  *No features fit within the current budget.*")
        lines.append("")

        lines.append("### 3. 🔴 FEATURES EXCLUDED")
        if sim['features_excluded']:
            for f in sim['features_excluded']:
                lines.append(f"  ✖ {f} (Requires additional budget)")
        else:
            lines.append("  *None.*")
        lines.append("")

        lines.append("### 4. ⭐ RECOMMENDED UPGRADES")
        add_amount = max(0, sim['options']['option2']['price'] - sim['options']['option1']['price'])
        unlocked = [f for f in sim['options']['option2']['features'] if f not in sim['options']['option1']['features']]
        lines.append(f"- **Recommended Budget**: ₹{sim['options']['option2']['price']:,}")
        lines.append(f"- **Additional Investment Needed**: ₹{add_amount:,}")
        lines.append(f"- **Additional Features Unlocked**: {', '.join(unlocked) if unlocked else 'None'}")
        lines.append("")

        lines.append("### 5. 💡 ROI & BUSINESS BENEFITS")
        lines.append(f"- **Business Value**: {sim['roi']['roi_statement']}")
        lines.append(f"- **Operational Savings**: {sim['roi']['ops_savings']}")
        lines.append("")

        lines.append("### 6. 📊 PACKAGE COMPARISON")
        lines.append("| Package | Target Price | Core Focus | Timeline | Support |")
        lines.append("| :--- | :--- | :--- | :--- | :--- |")
        for pkg_name, pkg in sim['packages'].items():
            lines.append(f"| **{pkg_name}** | ₹{pkg['price']:,} | {pkg['best_for'][:35]} | {pkg['timeline']} | {pkg['support']} |")
        lines.append("")

        lines.append("### 7. 🛠️ RECOMMENDED TECHNOLOGY STACK")
        lines.append(f"- **Platform / Architecture**: {sim['tech_stack']}")
        lines.append(f"- **Best Suited For**: {sim['best_for']}")
        lines.append("")

        lines.append("### 8. 🗺️ DEVELOPMENT ROADMAP")
        for p in sim['roadmap']:
            lines.append(f"- **{p['phase']}** (₹{p['cost']:,}): {p['details']} *({', '.join(p['features'])})*")
        lines.append("")

        lines.append("### 9. 💰 ITEMIZED COST BREAKDOWN")
        lines.append("Here is the detailed distribution of the development budget:")
        lines.append("| Component / Development Area | Investment Amount |")
        lines.append("| :--- | :--- |")
        for item in quotation.get("cost_breakdown", []):
            lines.append(f"| {item['item']} | ₹{item['amount']:,} |")
        lines.append(f"| **Grand Total (with taxes & support)** | **₹{quotation.get('total', 0):,}** |")
        lines.append("")

        lines.append("### 10. 🎛️ WHAT-IF BUDGET SIMULATION")
        lines.append("You can adjust the **Budget Simulator** slider or input field on the right side panel to dynamically see how shifting your budget scale changes included features, tech stacks, and delivery times in real-time!")
        lines.append("")

        lines.append("### 11. 📝 UPGRADE RECOMMENDATIONS")
        if sim['features_excluded']:
            lines.append("Based on your budget, I highly recommend launching **Phase 1 MVP** first. As user adoption grows, you can expand to subsequent phases to integrate advanced capabilities.")
        else:
            lines.append("Your budget fully covers the required scope. We can proceed with the ideal complete solution immediately.")
        lines.append("")

        lines.append("📄 **A detailed downloadable quotation and formal proposal have been synced to your dashboard.**")

        return "\n".join(lines)