# TechSoul Sales AI

An internal sales automation platform built for TechSoul AI. It handles the full client engagement lifecycle — from the first conversation to a signed proposal PDF — through a chatbot-driven interface backed by Google Gemini, a built-in CRM, and automated document generation.

Built with Flask, vanilla JS, SQLite, and the Gemini API.

---

## What It Does

A potential client lands on the site and starts a chat. The chatbot walks them through a structured consultation — collecting their name, company, contact info, project type, desired features, budget, and timeline. Once the conversation wraps up, the system:

1. Calculates a detailed quotation (base price + feature pricing + timeline multipliers + tax + maintenance)
2. Generates a tailored proposal with AI-written executive summaries and tech stack recommendations
3. Exports the proposal as a branded PDF
4. Saves the lead into the CRM with a calculated lead score
5. Optionally sends a follow-up email with the proposal attached

The admin dashboard gives the sales team visibility into all leads, proposals, conversation history, and pipeline analytics.

---

## Project Structure

```
├── backend/
│   ├── app.py                  # Flask application entry point
│   ├── config.py               # All application settings
│   ├── routes.py               # API + page routes (auth, chat, CRM, admin)
│   └── services/
│       ├── blueprint.py        # Project blueprint document generator
│       ├── crm.py              # Lead management, scoring, status tracking
│       ├── database.py         # SQLite schema, migrations, queries
│       ├── email_service.py    # SMTP email dispatch
│       ├── gemini_service.py   # Google Gemini API integration
│       ├── pdf_generator.py    # ReportLab PDF proposal builder
│       ├── pricing.py          # Quotation engine (base + features + modifiers)
│       ├── proposal.py         # Proposal assembly and AI content injection
│       └── response.py         # Standardized API response formatter
│
├── chatbot/
│   ├── chatbot.py              # Main controller — ties conversation + AI engines
│   ├── conversation.py         # State-driven conversation flow manager
│   ├── ai_engine.py            # Orchestrates pricing, proposals, and CRM writes
│   ├── prompt_engine.py        # Prompt templates for Gemini calls
│   ├── state_machine.py        # Enum-based conversation states
│   ├── memory.py               # In-session key-value store for collected data
│   └── validators.py           # Input validation (email, phone, budget, etc.)
│
├── frontend/
│   ├── static/
│   │   ├── css/                # Stylesheets (dashboard, chat, cards, themes)
│   │   ├── js/                 # Client-side logic (chat, UI, theme manager)
│   │   └── images/             # Logo, bot avatar, user avatar
│   └── templates/
│       ├── index.html          # Landing page
│       ├── dashboard.html      # Client portal
│       ├── admin.html          # Admin lead management dashboard
│       ├── login.html          # Authentication page
│       ├── register.html       # Registration page
│       └── components/         # Reusable template partials
│
├── data/
│   ├── pricing.json            # Feature and project pricing catalog
│   ├── proposals.json          # Generated proposal metadata
│   ├── crm.json                # Legacy CRM data (migrated to SQLite)
│   └── proposals/              # Exported PDF and DOCX proposal files
│
├── .env                        # API keys (not committed — see setup below)
├── .gitignore
└── requirements.txt
```

---

## Setup

### Prerequisites

- Python 3.10+
- pip
- A Google Gemini API key ([get one here](https://aistudio.google.com/apikey))

### Installation

```bash
# Clone the repo
git clone https://github.com/aj-techsoul/techsoul-sales-ai.git
cd techsoul-sales-ai

# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

The application reads this key at startup via `os.environ.get("GEMINI_API_KEY")` in `backend/config.py`.

### Run the Server

```bash
python backend/app.py
```

The app starts on `http://localhost:5000` by default.

---

## How the Chatbot Works

The conversation engine uses a finite state machine with these states:

```
WELCOME → ASK_NAME → ASK_COMPANY → ASK_EMAIL → ASK_PHONE
    → ASK_PROJECT → ASK_FEATURES → ASK_BUDGET → ASK_TIMELINE
    → GENERATE_QUOTE → SHOW_QUOTE → GENERATE_PROPOSAL → SEND_PROPOSAL
    → UPSELL → COMPLETED
```

At each state, user input is validated and stored in an in-memory key-value store (`ConversationMemory`). The `PromptEngine` builds structured prompts for Gemini to parse free-text responses into structured data — so a user can type "around 2 lakhs" and the system extracts `200000` as the budget value.

When the conversation reaches `GENERATE_QUOTE`, the pricing engine kicks in:

- Looks up the project type base price from `data/pricing.json`
- Adds individual feature prices
- Applies timeline multipliers (Urgent = 1.5x, Fast = 1.25x)
- Calculates GST and annual maintenance
- Runs budget optimization if the quoted price exceeds the stated budget

The proposal step calls Gemini to write an executive summary, scope of work, and technology recommendations specific to the client's project, then wraps everything into a branded PDF via ReportLab.

---

## CRM & Lead Scoring

Every completed consultation creates a lead record in SQLite. The scoring algorithm weighs:

| Factor               | Max Points | Logic                                    |
|----------------------|------------|------------------------------------------|
| Engagement baseline  | 30         | Awarded for starting a consultation      |
| Budget range         | 30         | ₹2.5L+ = 30, ₹1.5L+ = 20, ₹50K+ = 10  |
| Timeline urgency     | 20         | Urgent = 20, Fast = 10, Normal = 5       |
| Feature count        | 20         | 3 points per feature, capped at 20       |
| Profile completeness | 10         | Phone + Company + Email all provided      |

Leads are tracked through statuses: **New Lead → Contacted → Proposal Sent → Negotiation → Won / Lost**

The admin dashboard at `/admin` shows all leads in a sortable table with status filters, search, and individual lead detail views including full conversation history and generated proposals.

---

## Theme System

The frontend ships with 8 color themes (Blue, Pink, Sunset, Cyber, Nature, Cat, Dog, Dark) that apply globally via CSS custom properties. Themes persist through:

- **Guest users**: `localStorage` under the key `techsoul_theme`
- **Logged-in users**: Saved to the user's database record via `POST /api/auth/theme` and synced across sessions/devices

See [TESTING.md](TESTING.md) for detailed theme testing procedures.

---

## Key API Endpoints

| Method | Endpoint                   | Description                          |
|--------|----------------------------|--------------------------------------|
| POST   | `/api/chat`                | Send a chat message, get a response  |
| POST   | `/api/chat/start`          | Start a new conversation session     |
| GET    | `/api/dashboard/summary`   | User profile + project stats         |
| GET    | `/api/crm/clients`         | List all CRM leads (admin)           |
| GET    | `/api/crm/client/<id>`     | Single lead detail                   |
| POST   | `/api/auth/login`          | User authentication                  |
| POST   | `/api/auth/register`       | New user registration                |
| POST   | `/api/auth/theme`          | Save theme preference                |
| GET    | `/api/proposals/<file>`    | Download generated proposal PDF      |

---

## Tech Stack

| Layer     | Technology                                      |
|-----------|--------------------------------------------------|
| Backend   | Python 3, Flask, Flask-CORS                      |
| Database  | SQLite (via `sqlite3` stdlib)                    |
| AI        | Google Gemini 1.5 Flash (via `google-generativeai`) |
| PDF       | ReportLab                                        |
| Frontend  | Vanilla HTML/CSS/JS, Jinja2 templates            |
| Auth      | PBKDF2-SHA256 password hashing, Flask sessions   |

---

## License

Internal project. Not open-sourced.
