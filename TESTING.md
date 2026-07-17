# TechSoul AI - Theme System Testing Guide

This document outlines the testing procedures to verify the correctness, responsiveness, aesthetics, and persistence of the **TechSoul AI Theme System**.

---

## 🖥️ 1. Manual UI & Visual Styling Verification

Verify the visual layout and transition effects across all 8 custom color themes.

### A. Guest-Facing Theme Selector Modal
1. Navigate to the landing page (`http://127.0.0.1:5000/`).
2. Click the **Appearance** button in the left sidebar menu.
3. Check that the backdrop blurs smoothly (`backdrop-filter: blur(12px)`) and a card-styled modal popup appears.
4. **Hover Live Preview Check**:
   - Move the mouse over the **Nature Theme** card. Confirm that the entire workspace (backgrounds, headers, borders) changes immediately to sage and mint shades.
   - Move the mouse off the card. Confirm the workspace immediately reverts to the default *Blue Theme* colors without lag.
   - Hover over other themes (*Pink*, *Sunset*, *Cyber*, *Cat*, *Dog*, *Dark*) to verify their distinct palettes.
5. **Applying a Theme**:
   - Hover over the **Cyber Theme** card and click **Apply**.
   - Confirm that the active theme badge shows a green checkmark indicating `<i class="fa-solid fa-circle-check"></i> Active` and the modal buttons update.
   - Close the modal. Verify that neon magenta/cyan accents remain active.

### B. Client Portal Dashboard Tab
1. Sign in as a customer (or register a new client profile).
2. Navigate to **Settings** from the sidebar or dashboard menu.
3. Verify that the Settings panel split is responsive:
   - On Desktop: Profile details are on the left, and **Appearance Settings** (theme selection cards) are on the right in a grid.
   - On Mobile/Tablet: The cards stack vertically.
4. Click on any card (e.g. **Cat Theme**).
5. Verify that the changes apply **instantly** without reloading or refreshing the page.

### C. Chatbot Avatar Theme Adaptation
1. Open the Chat Interface on the landing page or dashboard.
2. Send a dummy message to start a conversation.
3. Observe the bot avatar pseudo-element icon (`.bot-message::before`):
   - **Blue / Pink / Sunset / Cyber Themes**: Verify a sleek futuristic assistant robot/AI icon is shown.
   - **Cat Theme**: Verify a custom FontAwesome cat icon is rendered.
   - **Dog Theme**: Verify a custom dog paw icon is rendered.
   - **Nature Theme**: Verify a custom seedling/leaf icon is rendered.

---

## 💾 2. Persistence & Multi-Device Sync Verification

Confirm that themes are cached client-side and saved database-side, syncing automatically upon login.

### A. Guest Local Storage Fallback
1. Access the site as a guest (logged out).
2. Open the browser Developer Console (`F12`), go to the **Application** (or **Storage**) tab, and expand **Local Storage**.
3. Open the Appearance modal and select the **Pink Theme**.
4. Confirm a new entry key `techsoul_theme` is created with the value `"pink"`.
5. Refresh the page. Verify the page renders immediately in the *Pink Theme* without flashing the default blue style (FOUC check).

### B. Logged-in Sync to User Profile Database
1. Login with a customer account (e.g. `client@techsoul.in`).
2. Go to settings and apply the **Nature Theme**.
3. Confirm that an API call to `POST /api/auth/theme` was sent successfully with `{"theme": "nature"}` in the payload.
4. Log out. Confirm the page reverts to the guest theme or default.
5. Log back in. Confirm that the **Nature Theme** is pulled from the database user row and applied automatically on load.

### C. Multi-Device/Cross-Browser Sync
1. Open Google Chrome, log in, and switch the theme to **Sunset Theme**.
2. Open Microsoft Edge, Safari, or an Incognito tab, and log in with the *same* user account.
3. Verify that the **Sunset Theme** is loaded and applied instantly on the second browser session.

---

## 🔌 3. Endpoint & Console Script Testing

Verify the backend routing and API responses programmatically.

### A. Theme POST API Endpoint
Execute this script inside the browser developer console (`F12`) to verify the backend theme save endpoint responds correctly:

```javascript
fetch('/api/auth/theme', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ theme: 'cyber' })
})
.then(res => res.json())
.then(data => console.log('API Theme Save Result:', data))
.catch(err => console.error('Error saving theme:', err));
```

**Expected Console Output (Logged In):**
```json
API Theme Save Result: { "status": "success", "message": "Theme updated to cyber" }
```

**Expected Console Output (Guest User):**
```json
API Theme Save Result: { "status": "success", "message": "Theme updated in session for guest" }
```

### B. Dashboard Summary Endpoint
Verify that user profiles include the `theme` parameter on retrieve:

```javascript
fetch('/api/dashboard/summary')
.then(res => res.json())
.then(data => console.log('User Profile Summary:', data.profile))
.catch(err => console.error('Error:', err));
```

**Expected Console Output:**
Confirm the logged-in profile metadata contains the `theme` field matching the applied theme:
```json
{
  "id": 1,
  "name": "Client Name",
  "email": "client@techsoul.in",
  "company": "Client Company",
  "theme": "cyber"
}
```

---

## 🐍 4. Backend Client Script Test

You can check Flask application stability using the included mock test client:

```bash
# Run Flask test client
python test_flask_client.py
```

This runs request simulations against the routes and prints response statuses, verifying that page layouts continue to render correctly with the theme engine enabled.
