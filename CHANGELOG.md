# Changelog

All notable changes to this project.

---

## [1.0.0] — 2026-07-17

### Initial Release

**Chatbot Engine**
- Finite state machine conversation flow covering client details, project requirements, budget, and timeline collection.
- Google Gemini 1.5 Flash integration for natural language parsing, budget optimization suggestions, and AI-written proposal sections.
- Prompt engineering layer with structured templates for each conversation state.
- Input validation for email, phone (international E.164 format), budget ranges, and free-text fields.
- Returning user detection — skips already-known fields and greets by name.

**Pricing & Quotation**
- Configurable pricing catalog via `data/pricing.json` with per-project and per-feature pricing.
- Timeline multipliers (Normal 1x, Fast 1.25x, Urgent 1.5x).
- GST calculation and annual maintenance cost estimation.
- Budget optimization mode — automatically suggests feature trimming when quoted price exceeds stated budget.
- Upsell recommendations when budget has headroom.

**Proposal Generation**
- Automated proposal assembly with AI-generated executive summary, scope of work, and technology stack recommendations.
- Branded PDF export via ReportLab with pricing tables, milestone payment schedules, and warranty terms.
- Project blueprint document generation (DOCX + PDF).
- Proposals indexed in `data/proposals.json` and downloadable from the dashboard.

**CRM & Lead Management**
- SQLite-backed lead storage with automatic migration from legacy JSON format.
- Lead scoring algorithm (0–100) based on budget, timeline urgency, feature count, and profile completeness.
- Lead status pipeline: New Lead → Contacted → Proposal Sent → Negotiation → Won / Lost.
- Admin dashboard with sortable lead table, search, status filters, and individual lead detail views.
- Full conversation history stored and viewable per lead.

**User Authentication**
- Registration and login with PBKDF2-SHA256 password hashing (16-byte random salt, 100K iterations).
- Flask session management with role-based access (admin vs client).
- International phone number validation via `phonenumbers` library with regex fallback.

**Frontend**
- Landing page with embedded chat widget.
- Client dashboard portal with project overview, proposal downloads, and profile settings.
- Admin CRM dashboard with lead analytics and management tools.
- 8 color themes (Blue, Pink, Sunset, Cyber, Nature, Cat, Dog, Dark) with live preview on hover.
- Theme persistence via localStorage for guests, database sync for logged-in users.
- Responsive layout with mobile/tablet breakpoints.

**Email**
- SMTP integration for automated proposal delivery.
- Configurable email credentials via `backend/config.py`.
