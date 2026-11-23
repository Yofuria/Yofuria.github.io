(() => {
    const key = 'yofuria-color-theme';
    const system = window.matchMedia('(prefers-color-scheme: dark)');
    const root = document.documentElement;
    let preference = null;
    let button;

    try {
        preference = window.localStorage.getItem(key);
    } catch {
        // The switch can still work for this page when storage is unavailable.
    }

    function applyTheme() {
        const dark = preference === 'dark' || (preference !== 'light' && system.matches);
        root.dataset.theme = dark ? 'dark' : 'light';
        if (button) {
            const next = dark ? 'Day' : 'Night';
            button.querySelector('span').textContent = next;
            button.title = 'Switch to ' + next.toLowerCase() + ' mode';
            button.setAttribute('aria-label', button.title);
        }
    }

    // Set the palette in the head so navigation doesn't flash the other theme.
    applyTheme();

    document.addEventListener('DOMContentLoaded', () => {
        button = document.querySelector('.ah-theme-toggle');
        if (!button) return;
        applyTheme();
        button.hidden = false;
        button.addEventListener('click', () => {
            preference = root.dataset.theme === 'dark' ? 'light' : 'dark';
            applyTheme();
            try {
                window.localStorage.setItem(key, preference);
            } catch {
                // Keep the selection in memory for this visit.
            }
        });
    });

    system.addEventListener('change', applyTheme);
    window.addEventListener('storage', event => {
        if (event.key === key || event.key === null) {
            preference = event.newValue;
            applyTheme();
        }
    });
})();
