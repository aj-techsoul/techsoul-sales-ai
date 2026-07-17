# TechSoul Sales AI

TechSoul Sales AI is an intelligent sales automation platform and interactive chatbot assistant. It integrates Gemini AI services, a dynamic state machine chatbot, and a full-stack Flask application equipped with CRM management, automatic PDF/DOCX proposal generation, email outreach, and a premium 8-theme UI styling system.

---

## 🌟 Key Features

*   **Intelligent Sales Chatbot (`/chatbot`)**: Built with a robust conversational state machine, memory management, input validation, and customizable AI prompt engines.
*   **CRM & Proposal Automation**: Automatically processes client interactions, references custom pricing sheets, updates client CRM profiles, and generates professional PDFs/DOCX proposals (blueprints).
*   **Gemini LLM Integration**: Uses Google Gemini API services for state-of-the-art responses, custom proposal copywriting, and context-aware chat behavior.
*   **Premium Theme Engine (8 Custom Themes)**:
    *   Sleek guest & client interface options: *Blue*, *Pink*, *Sunset*, *Cyber*, *Cat*, *Dog*, *Nature*, and *Dark*.
    *   Features smooth backdrop blurs, instant preview, local storage caching, and database profile synchronization.
    *   Responsive split-column layout adaptions for desktop, tablet, and mobile screens.
*   **Secure Authentication**: Multi-role login (Client & Admin dashboards) with theme persistence.

---

## 📂 Repository Structure

```
├── backend/
│   ├── app.py                     # Flask application entry point
│   ├── config.py                  # App configuration settings
│   ├── routes.py                  # API endpoints and page routings
│   └── services/                  # Business logic (Gemini, CRM, PDF, Email, Pricing)
├── chatbot/
│   ├── ai_engine.py               # Core LLM prompt interactions
│   ├── chatbot.py                 # Main Chatbot interface
│   ├── memory.py                  # Session and chat state memories
│   ├── prompt_engine.py           # Prompt assembly utilities
│   ├── state_machine.py           # Conversational flow state manager
│   └── validators.py              # User-input validators
├── data/                          # CRM files, pricing configurations, and generated proposals
├── frontend/
│   ├── static/                    # Custom CSS theme assets, icons, and JS logic
│   └── templates/                 # Jinja2 templates (dashboard, chat panel, sidebar)
├── requirements.txt               # Project python dependencies
├── test_flask_client.py           # Automated route simulation tests
└── TESTING.md                     # Theme system verification guide
```

---

## ⚙️ Getting Started

### Prerequisites
- Python 3.8 or higher
- Pip

### 1. Installation
Clone the repository and navigate into the project directory:
```bash
git clone https://github.com/aj-techsoul/techsoul-sales-AI.git
cd techsoul-sales-AI
```

Create a virtual environment and activate it:
```bash
# MacOS / Linux
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file in the root directory (or set environment variables) with:
```env
FLASK_ENV=development
SECRET_KEY=your_secret_key_here
GEMINI_API_KEY=your_gemini_api_key
```

### 3. Run the Server
Launch the Flask development server:
```bash
python backend/app.py
```
Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your web browser.

---

## 🧪 Testing

We include a test client utility to verify route performance and app stability under the theme engine:
```bash
python test_flask_client.py
```

For manual visual testing, interactive terminal scripts, and client database sync checks, please refer to the detailed [TESTING.md](file:///Users/aj/Downloads/TechSoul-AI/techsoul-sales-ai/TESTING.md) guide.

---

## 📄 License
This project is licensed under the terms of the [LICENSE](file:///Users/aj/Downloads/TechSoul-AI/techsoul-sales-ai/LICENSE) file included in this repository.
