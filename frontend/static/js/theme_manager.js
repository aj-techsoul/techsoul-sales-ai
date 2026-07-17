/* ==========================================================
   TechSoul AI - Centralized Theme Manager
   Handles local storage, server sync, and hover preview logic
========================================================== */

const ThemeManager = {
    storageKey: 'techsoul_theme',
    currentTheme: 'blue',

    init: function(sessionTheme) {
        // Resolve theme priority: 
        // 1. Session theme (set by server)
        // 2. Local storage theme (saved locally)
        // 3. Default ('blue')
        const localTheme = localStorage.getItem(this.storageKey);
        this.currentTheme = sessionTheme || localTheme || 'blue';

        // Apply immediately
        this.applyTheme(this.currentTheme);

        // Sync local storage if server provided a theme
        if (sessionTheme && sessionTheme !== localTheme) {
            localStorage.setItem(this.storageKey, sessionTheme);
        }
        // Sync server if local theme exists but server doesn't know it yet
        if (!sessionTheme && localTheme && localTheme !== 'blue') {
            this.syncWithServer(localTheme);
        }
    },

    applyTheme: function(themeName) {
        document.documentElement.setAttribute('data-theme', themeName);
        document.body.setAttribute('data-theme', themeName);
        
        // Sync active state indicators for any theme cards present in the DOM
        this.updateUIElements(themeName);

        // Broadcast custom event so components can adjust (e.g. charts)
        const event = new CustomEvent('themechanged', { detail: { theme: themeName } });
        window.dispatchEvent(event);
    },

    updateUIElements: function(themeName) {
        const themeCards = document.querySelectorAll('.theme-card');
        themeCards.forEach(card => {
            const cardTheme = card.getAttribute('data-theme-name');
            const badge = card.querySelector('.active-badge');
            const btn = card.querySelector('.theme-apply-btn');
            
            if (cardTheme === themeName) {
                card.classList.add('active-theme-card');
                if (badge) badge.style.display = 'inline-block';
                if (btn) btn.style.display = 'none';
            } else {
                card.classList.remove('active-theme-card');
                if (badge) badge.style.display = 'none';
                if (btn) btn.style.display = 'inline-block';
            }
        });
    },

    setTheme: function(themeName) {
        this.currentTheme = themeName;
        localStorage.setItem(this.storageKey, themeName);
        this.applyTheme(themeName);
        this.syncWithServer(themeName);
    },

    previewTheme: function(themeName) {
        // Temporarily apply theme (hover preview)
        document.documentElement.setAttribute('data-theme', themeName);
        document.body.setAttribute('data-theme', themeName);
        
        // Sync card active states for live hover feedback
        this.updateUIElements(themeName);
    },

    revertPreview: function() {
        // Revert to saved theme
        this.applyTheme(this.currentTheme);
    },

    syncWithServer: function(themeName) {
        fetch('/api/auth/theme', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ theme: themeName })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                console.log('Theme synchronized with server: ' + themeName);
            }
        })
        .catch(err => {
            console.error('Failed to sync theme with server:', err);
        });
    }
};
