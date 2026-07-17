# Contributing

Guidelines for working on this codebase.

---

## Branch Naming

Use descriptive branch names that indicate the scope of the change:

```
feature/upsell-flow
fix/phone-validation-regex
refactor/pricing-engine
```

Keep branches short-lived. Merge into `main` when the feature is stable and tested.

---

## Code Style

### Python

- Follow PEP 8 for formatting and naming conventions.
- Use docstrings on all public classes and methods. We use NumPy-style docstrings (`Parameters`, `Returns`, `Raises` sections).
- Keep imports organized: stdlib first, then third-party packages, then local modules. Separate each group with a blank line.
- Avoid wildcard imports (`from module import *`).

### JavaScript

- Use `const` and `let` — no `var`.
- Prefix DOM query results with a descriptive name (`const chatInput = document.getElementById(...)` not `const el = ...`).
- Event listeners go in a dedicated initialization block, not scattered across the file.

### HTML / Jinja2

- Reusable layout blocks go in `frontend/templates/components/`.
- Keep inline styles to zero. All styling goes through CSS files in `frontend/static/css/`.

---

## Adding a New Backend Service

1. Create a new file under `backend/services/`.
2. Write a class with a clear single responsibility (e.g., `NotificationService`).
3. Import and instantiate it where needed — typically in `routes.py` or `ai_engine.py`.
4. Add any new configuration keys to `backend/config.py` with a descriptive comment block.

---

## Adding a New Chatbot State

1. Add the new state to the `ChatState` enum in `chatbot/state_machine.py`.
2. Add the handler logic in `chatbot/conversation.py` inside the `process_input()` method.
3. If the state requires AI parsing, add or update prompt templates in `chatbot/prompt_engine.py`.
4. If the state requires input validation, add a validator method in `chatbot/validators.py`.

---

## Environment & Secrets

- Never commit API keys, passwords, or tokens to the repository.
- All secrets go in the `.env` file (which is in `.gitignore`).
- Reference secrets in code via `os.environ.get("KEY_NAME")`.

---

## Commit Messages

Write commits in imperative mood, describing *what* the commit does:

```
Add budget optimization fallback for low-budget clients
Fix email validation rejecting valid .co.in domains
Remove hardcoded Gemini API key from config
```

Avoid vague messages like "fix stuff" or "update files".

---

## Testing

Before pushing any changes:

1. Start the server locally and run through a full chatbot conversation end to end.
2. Verify the admin dashboard loads and displays lead data correctly.
3. If you touched the pricing engine, cross-check at least two quotation outputs against manual calculations.
4. If you touched theming, follow the procedures in [TESTING.md](TESTING.md).
