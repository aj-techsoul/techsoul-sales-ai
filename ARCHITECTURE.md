# Architecture

Technical overview of how the major pieces fit together.

---

## High-Level Flow

```
Client Browser
    │
    ├── Landing Page (index.html)
    │       │
    │       └── Chat Widget ──► POST /api/chat ──► Flask Routes
    │                                                   │
    │                                          TechSoulChatbot
    │                                           ├── ConversationEngine
    │                                           │     ├── StateMachine (state transitions)
    │                                           │     ├── Memory (key-value store)
    │                                           │     ├── Validators (input checks)
    │                                           │     └── PromptEngine (Gemini prompts)
    │                                           │
    │                                           └── AIEngine
    │                                                 ├── PricingService (quotation math)
    │                                                 ├── ProposalService (document assembly)
    │                                                 ├── GeminiService (AI content generation)
    │                                                 ├── PDFGenerator (ReportLab output)
    │                                                 └── CRMService (lead persistence)
    │
    ├── Client Dashboard (dashboard.html)
    │       └── REST API calls ──► /api/dashboard/* ──► DatabaseService ──► SQLite
    │
    └── Admin Dashboard (admin.html)
            └── REST API calls ──► /api/crm/* ──► CRMService ──► SQLite
```

---

## Backend Layer

### Flask Application (`backend/app.py`)

The entry point. Creates the Flask app instance, enables CORS, registers all API routes via `register_routes(app)`, and serves the Jinja2 templates from `frontend/templates/` with static assets from `frontend/static/`.

### Routes (`backend/routes.py`)

Single file handling all HTTP endpoints. Grouped by responsibility:

- **Authentication**: Registration, login, logout, session management. Passwords are hashed with PBKDF2-SHA256 (100,000 iterations, random 16-byte salt).
- **Chat**: Starting sessions, processing messages, retrieving conversation history.
- **Dashboard**: Profile data, project summaries, proposal downloads.
- **CRM/Admin**: Lead listing, detail views, status updates, analytics aggregation.
- **File Management**: Proposal PDF serving, file uploads with extension whitelisting.

### Services (`backend/services/`)

Each service is a standalone class with no cross-dependencies between services (they share config imports but don't import each other, with the exception of `ProposalService` calling `GeminiService` for AI-written sections).

| Service            | Responsibility                                                        |
|--------------------|-----------------------------------------------------------------------|
| `DatabaseService`  | SQLite connection pooling, schema creation, migrations from legacy JSON |
| `CRMService`       | Lead CRUD, scoring algorithm, status management                       |
| `PricingService`   | Quotation calculation from `pricing.json` catalog                     |
| `ProposalService`  | Proposal dict assembly, calls Gemini for written sections             |
| `GeminiService`    | All Gemini API calls — chat parsing, budget optimization, proposal copy |
| `PDFGenerator`     | ReportLab document builder for branded proposal PDFs                  |
| `EmailService`     | SMTP dispatch for proposal delivery                                   |
| `BlueprintService` | Project blueprint/scope document generation                           |

---

## Chatbot Layer

### State Machine

The conversation is modeled as a finite state machine defined in `chatbot/state_machine.py`. Each state maps to a specific piece of information being collected or an action being performed.

State transitions happen linearly for the core flow, with conditional branching for:
- Upsell offers (if the quoted price is under budget)
- Budget optimization (if the quoted price exceeds stated budget)
- Returning user shortcuts (skipping already-known fields)

### Conversation Engine (`chatbot/conversation.py`)

The main loop. For each incoming message:

1. Current state determines what we're expecting
2. Input is validated by `Validator` methods
3. If valid, data is stored in `ConversationMemory`
4. State advances to the next step
5. A response message is constructed (sometimes with Gemini's help via `PromptEngine`)

### Memory (`chatbot/memory.py`)

A simple dictionary-backed store scoped to the current session. Holds collected fields like `name`, `email`, `project`, `features`, `budget`, `timeline`. Gets wiped on `reset()`.

### Prompt Engine (`chatbot/prompt_engine.py`)

Builds structured prompt strings for Gemini API calls. Each prompt type has a template that injects the current conversation context, client data, and specific instructions for what Gemini should extract or generate.

---

## Data Layer

### SQLite (`data/techsoul.db`)

Primary data store. Schema includes:

- `users` — registered accounts with hashed passwords, profile data, theme preference
- `leads` — CRM records with scoring, status, contact info
- `conversations` — full chat history per session
- `projects` — project metadata linked to users
- `proposals` — generated proposal records with file paths
- `notifications` — in-app notification queue

The `DatabaseService` handles automatic schema creation on first run and data migration from the legacy JSON file format (`clients.json`).

### JSON Files (`data/`)

- `pricing.json` — the pricing catalog. Defines base prices per project type and per-feature pricing with categories.
- `proposals.json` — lightweight index of generated proposals.
- `crm.json` — legacy format, kept for backward compatibility during migration.

---

## Frontend Layer

Server-rendered Jinja2 templates with client-side interactivity via vanilla JavaScript.

### Pages

| Page              | Purpose                                    |
|-------------------|--------------------------------------------|
| `index.html`      | Landing page with embedded chat widget     |
| `dashboard.html`  | Client portal (projects, proposals, settings) |
| `admin.html`      | Admin CRM dashboard (leads, analytics)     |
| `login.html`      | Authentication form                        |
| `register.html`   | Registration form                          |

### CSS Architecture

Stylesheets are split by concern:
- `style.css` — base layout, typography, global rules
- `dashboard.css` — dashboard-specific layout
- `chat.css` — chat widget styling
- `cards.css` — card component styles
- `themes.css` — CSS custom property definitions for all 8 themes
- `responsive.css` — breakpoint overrides

### JavaScript Modules

- `chat.js` — handles message sending, response rendering, typing indicators
- `script.js` — dashboard initialization, sidebar navigation, data fetching
- `cards.js` — project and feature card rendering
- `summary.js` — dashboard summary statistics
- `theme_manager.js` — theme switching, persistence (localStorage + API sync)
- `ui.js` — shared UI utilities (modals, toasts, loading states)

---

## Authentication

- Passwords are hashed using PBKDF2-HMAC-SHA256 with a random 16-byte salt and 100,000 iterations.
- Sessions are managed via Flask's built-in session cookies.
- The admin dashboard is access-controlled by checking the user's `role` field in the database (`admin` vs `client`).
- Phone numbers are validated using the `phonenumbers` library with a regex fallback for E.164 format compliance.
