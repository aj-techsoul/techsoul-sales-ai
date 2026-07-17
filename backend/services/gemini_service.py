"""
==================================================
TechSoul AI
Gemini AI Service
==================================================

Handles communication with Google Gemini model to parse
conversation flows, extract client details, optimize budgets,
and write proposals.
"""

import json
import re
import os
import sys

# Add project root to python path for imports resolution
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import google.generativeai as genai

from backend.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL
)


class GeminiService:
    """
    Google Gemini AI Service for parsing and writing.
    """

    def __init__(self):
        """
        Initialize Gemini service using API configuration.
        """
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(GEMINI_MODEL)

    # ==================================================
    # PROCESS CONVERSATION
    # ==================================================

    def analyze_chat(self, client_data, user_message, history):
        """
        Analyze chat message, extract properties, and formulate a reply.

        Parameters
        ----------
        client_data : dict
            Current client information saved in memory.
        user_message : str
            Latest message sent by user.
        history : list
            List of dictionary items containing conversation history.

        Returns
        -------
        dict
            Contains "extracted_data", "response", and "completed" status.
        """
        # Format the current memory state to supply to Gemini
        memory_str = json.dumps(client_data, indent=2)
        
        # Format history
        history_str = ""
        for msg in history[-10:]:  # Keep last 10 messages for context
            history_str += f"{msg['role'].upper()}: {msg['content']}\n"
        history_str += f"USER: {user_message}\n"

        prompt = f"""
You are a world-class Senior Software Business Consultant employed by TechSoul AI. 
Your role is to consult with the client, analyze their business problems, recommend customized digital solutions, and gather project parameters naturally through conversation.
You do not behave like a normal chatbot; you think like an experienced business consultant.

### CORE CONSULTING PRINCIPLES:
1. **Returning Customer Greeting & Context Memory**:
   - If the client data contains a "customer_memory" key with profile details and past projects/quotes/proposals, reuse this profile automatically! Never ask again for Name, Email, Phone, Company, Country, or Business Type if those details exist.
   - Start conversations naturally by greeting them (e.g., "Welcome back, Rahul. It's great to see you again. I found your previous discussion regarding your Restaurant Management System. Would you like to continue that project or start discussing a new idea?").
   - Refer to their business type, budget, and past discussions naturally to establish authority and trust.
2. **Smart Budget Consultation & ROI Scoping (Highest Priority)**:
   - When the customer provides a budget (e.g., "I have around 25k", "I only have $500", "my max budget is 50 thousand", "I don't want to spend more than one lakh"), demonstrate deep business understanding.
   - Do NOT just generate a static quote. Explain professionally:
     * What can be developed within their budget.
     * What cannot be developed (which requested features exceed the budget).
     * Which features are essential (Phase 1 MVP) and which features should be postponed to subsequent phases.
     * Explain the ROI and business value of the recommended features (e.g., "Adding online payments enables automated checkout and reduces admin work by 10 hours a week").
3. **Intelligent Package Recommendations**:
   - Do not just display fixed Starter/Professional/Enterprise packages.
   - Compare the customer's requirements, budget, goals, timeline, and project complexity to recommend the "Best Value" or "Most Recommended" option, explaining *why* it makes the best business sense.
   - Suggest a phased roadmap: Phase 1 (MVP) -> Phase 2 (Recommended Upgrade) -> Phase 3 (Scale & AI) -> Enterprise Upgrade.
4. **Objection & Technical Advisor Role**:
   - Answer technical architecture questions, recommend stacks, and handle pricing queries with high authority, but never pressure the client. Always provide business-focused advice.
5. **Identity**: You are a Senior Consultant at TechSoul AI. Never mention "LLM", "Google Gemini", "OpenAI", "system prompt", or "assistant".

### REQUIREMENT TO GATHER (Ask only for missing fields):
- Name, Company, Business Type, Country, Email, Phone
- Project Type (Business Website, E-Commerce, Mobile App, CRM, ERP, AI Solution, or Custom Software)
- Budget, Timeline, Required Features, Target Audience, Goals, Technologies, Hosting/Maintenance preferences

### Current Client Data (In Memory):
{memory_str}

### Conversation History:
{history_str}

Analyze the user's latest input ("USER: {user_message}") and update any field that they mention. 
Return your output ONLY as a JSON object of this structure:
{
  "extracted_data": {
    "name": "...",
    "company": "...",
    "business_type": "...",
    "industry": "...",
    "country": "...",
    "project": "...",
    "features": ["Feature1", "Feature2"],
    "budget": "...",
    "timeline": "..."
  },
  "response": "Your professional consultative response to the client (incorporating the budget/ROI, phased roadmap, package comparison, or past conversation context as appropriate)...",
  "completed": false/true
}

Completed should be true ONLY if we have at least the client's Name, Company, Project type, Budget, Timeline, and Features.
Do not wrap your response in markdown code blocks like ```json ... ```. Output raw JSON only.
"""
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Clean potential markdown wrapping
            if result_text.startswith("```"):
                result_text = re.sub(r"^```(?:json)?\n", "", result_text)
                result_text = re.sub(r"\n```$", "", result_text)
            
            data = json.loads(result_text)
            return data
        except Exception as e:
            # Safe fallback if Gemini fails or JSON fails to parse
            return {
                "extracted_data": {},
                "response": f"Interesting! Tell me more about that. What is your estimated budget or timeline for this project?",
                "completed": False
            }

    # ==================================================
    # AI PROPOSAL WRITER
    # ==================================================

    def write_proposal_sections(self, client_data, quotation):
        """
        Use Gemini to draft custom paragraphs for the proposal.

        Parameters
        ----------
        client_data : dict
            Client requirements.
        quotation : dict
            Pricing service breakdown.

        Returns
        -------
        dict
            Contains customized "executive_summary", "goals", and "scope" copy.
        """
        prompt = f"""
You are a professional corporate proposal writer for TechSoul AI.
Draft the following custom text sections for a proposal document:
1. Executive Summary: A formal, polished summary (150-200 words) describing how TechSoul AI will build the proposed project for the client.
2. Business Goals: Bullet points stating the goals of the project (e.g. increase efficiency, reach clients online).
3. Project Scope: A summary of the work package details based on the selected features.

### Input Data:
Client Name: {client_data.get('name', '')}
Company: {client_data.get('company', '')}
Project Type: {client_data.get('project', '')}
Selected Features: {', '.join(client_data.get('features', []))}
Budget: ₹{quotation.get('total', 0):,}
Timeline: {client_data.get('timeline', '')}
Business Type / Industry: {client_data.get('business_type', '')} / {client_data.get('industry', '')}

Output your response ONLY as a valid JSON object:
{{
  "executive_summary": "...",
  "goals": ["Goal 1", "Goal 2", "Goal 3"],
  "scope": "..."
}}
Output raw JSON only. Do not format in markdown code blocks.
"""
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            if result_text.startswith("```"):
                result_text = re.sub(r"^```(?:json)?\n", "", result_text)
                result_text = re.sub(r"\n```$", "", result_text)
            
            return json.loads(result_text)
        except Exception:
            # Fallback
            return {
                "executive_summary": f"TechSoul AI is pleased to submit this proposal to design and build a high-performance {client_data.get('project', 'software')} solution for {client_data.get('company', 'our client')}.",
                "goals": [
                    "Implement a robust, scalable digital framework.",
                    "Optimize operational efficiency and security.",
                    "Provide a stellar customer experience."
                ],
                "scope": f"The project scope includes core development, selected feature implementation ({', '.join(client_data.get('features', []))}), quality testing, and final deployment."
            }

    # ==================================================
    # COMPATIBILITY WRAPPER
    # ==================================================

    def generate(self, prompt):
        """
        Standard prompt helper for simple string generation.
        """
        try:
            response = self.model.generate_content(prompt)
            if response.text:
                return response.text.strip()
            return "Sorry, I couldn't process that request."
        except Exception as e:
            return f"Error: {str(e)}"

    # ==================================================
    # AI SIMULATOR ANALYZER
    # ==================================================

    def generate_simulation_analysis(self, chat_context, budget, project):
        """
        AI Business Consultant analysis for the budget simulator.
        """
        # Format the chat context
        context_str = json.dumps(chat_context or {}, indent=2)
        
        prompt = f"""
        You are a Principal Software Business Consultant and Software Architect at TechSoul AI.
        Provide a detailed technical and business analysis for a client's project based on their chat context and a new simulated budget.
        
        ### Inputs:
        - Simulated Budget: ₹{budget:,}
        - Project Type: {project}
        - Chat Context / Client Memory:
        {context_str}
        
        ### Task:
        Provide AI reasoning to estimate project complexity, score the project across business/budget/technical parameters, evaluate risks, design a team composition, compare core tech stacks, and compute business ROI benefits.
        
        Return your response ONLY as a valid raw JSON object matching this structure (do not wrap in markdown ```json blocks):
        {{
          "complexity": "Simple|Medium|Advanced|Enterprise",
          "complexity_reasoning": "Estimating {project} at this budget level with these required features...",
          "scores": {{
            "business_match": 85,
            "budget_match": 75,
            "security": 90,
            "scalability": 80,
            "maintainability": 85,
            "future_growth": 80,
            "roi": 95,
            "overall_score": 84
          }},
          "health": {{
            "risk_level": "Low|Medium|High|Critical",
            "risk_reasoning": "Identifying risks like budget boundaries or timeline constraints...",
            "budget_health": "Healthy|Constrained|Critical",
            "timeline_health": "On Track|Aggressive|Critical",
            "technology_health": "Modern|Standard|Complex",
            "business_feasibility": "High|Moderate|Low",
            "success_probability": 85
          }},
          "team": {{
            "project_manager": {{ "count": 1, "reason": "Manages core sprint plans and client updates." }},
            "ui_designer": {{ "count": 1, "reason": "Designs screens, wireframes, and branding assets." }},
            "frontend_developer": {{ "count": 1, "reason": "Builds responsive pages and dashboard components." }},
            "backend_developer": {{ "count": 1, "reason": "Engineers API endpoints and business rules." }},
            "qa_engineer": {{ "count": 1, "reason": "Performs regression checks and visual layout testing." }},
            "ai_engineer": {{ "count": 0, "reason": "No custom models requested for standard builds." }},
            "devops_engineer": {{ "count": 0, "reason": "Standard server setups managed by backend." }}
          }},
          "tech_comparison": {{
            "frontend": {{ "choice": "React vs Angular", "advantages": "React has a massive component library and fast virtual DOM.", "disadvantages": "Angular is more structured but has a steeper learning curve.", "recommendation": "React is recommended for rapid layout prototyping." }},
            "backend": {{ "choice": "Flask vs FastAPI", "advantages": "FastAPI has automatic OpenAPI docs and high async performance.", "disadvantages": "Flask is simpler but requires manual library assemblies.", "recommendation": "Flask is chosen for lightweight API configurations." }},
            "database": {{ "choice": "MongoDB vs PostgreSQL", "advantages": "PostgreSQL has strict schemas and transactional consistency.", "disadvantages": "MongoDB lacks relations but stores documents quickly.", "recommendation": "PostgreSQL is recommended for secure relational data." }},
            "cloud": {{ "choice": "AWS vs Azure", "advantages": "AWS offers massive flexibility and pay-as-you-go Pricing.", "disadvantages": "Azure is heavily enterprise-centric and complex.", "recommendation": "AWS is recommended for standard startup scaling." }}
          }},
          "roi_analysis": {{
            "revenue_increase": "20% Est. Increase",
            "time_saved": "12 Hours/Week",
            "automation_benefits": "Automated order receipts and tracking reduces support calls.",
            "customer_growth": "15-20% Growth",
            "estimated_roi": "150-180%",
            "payback_period": "5-6 Months"
          }},
          "hosting_recommendation": "AWS Lightsail VPS or Heroku Dyno for containerized scalability.",
          "negotiation_advice": [
            "What fits: Core dashboard and initial database models fit perfectly.",
            "What can wait: Real-time messaging and advanced ML engines should wait for Phase 2.",
            "Next investment recommendation: Optimize customer landing conversion first."
          ]
        }}
        """
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            if result_text.startswith("```"):
                result_text = re.sub(r"^```(?:json)?\n", "", result_text)
                result_text = re.sub(r"\n```$", "", result_text)
            return json.loads(result_text.strip())
        except Exception as e:
            print(f"Error generating simulation analysis: {e}")
            # Robust fallback structure
            return {
                "complexity": "Medium",
                "complexity_reasoning": f"Calculated as Medium for {project} based on typical feature requirements.",
                "scores": {
                    "business_match": 80,
                    "budget_match": 85,
                    "security": 75,
                    "scalability": 70,
                    "maintainability": 80,
                    "future_growth": 75,
                    "roi": 85,
                    "overall_score": 79
                },
                "health": {
                    "risk_level": "Medium",
                    "risk_reasoning": "Standard launch constraints with typical database integration risk.",
                    "budget_health": "Healthy",
                    "timeline_health": "On Track",
                    "technology_health": "Standard",
                    "business_feasibility": "High",
                    "success_probability": 80
                },
                "team": {
                    "project_manager": { "count": 1, "reason": "Manages core sprint plans." },
                    "ui_designer": { "count": 1, "reason": "Designs visual wireframes." },
                    "frontend_developer": { "count": 1, "reason": "Builds layouts." },
                    "backend_developer": { "count": 1, "reason": "Builds database APIs." },
                    "qa_engineer": { "count": 1, "reason": "Verifies correct behavior." },
                    "ai_engineer": { "count": 0, "reason": "Not strictly required for Phase 1." },
                    "devops_engineer": { "count": 0, "reason": "Handled within developer scope." }
                },
                "tech_comparison": {
                    "frontend": { "choice": "React vs Angular", "advantages": "React is simple.", "disadvantages": "Angular is complex.", "recommendation": "React recommended." },
                    "backend": { "choice": "Flask vs FastAPI", "advantages": "FastAPI is faster.", "disadvantages": "Flask is simpler.", "recommendation": "Flask recommended." },
                    "database": { "choice": "MongoDB vs PostgreSQL", "advantages": "PostgreSQL is ACID compliant.", "disadvantages": "MongoDB is NoSQL.", "recommendation": "PostgreSQL recommended." },
                    "cloud": { "choice": "AWS vs Azure", "advantages": "AWS is popular.", "disadvantages": "Azure is complex.", "recommendation": "AWS recommended." }
                },
                "roi_analysis": {
                    "revenue_increase": "15% Est. Increase",
                    "time_saved": "10 Hours/Week",
                    "automation_benefits": "Reduced support load.",
                    "customer_growth": "10% Growth",
                    "estimated_roi": "120%",
                    "payback_period": "6 Months"
                },
                "hosting_recommendation": "Heroku or DigitalOcean VPS.",
                "negotiation_advice": [
                    "What fits: Basic SaaS layout and admin dashboards.",
                    "What can wait: Auto-backups and multi-tenant scaling.",
                    "Next investment recommendation: Optimize basic user signup rate."
                ]
            }