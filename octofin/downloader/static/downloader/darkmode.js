function setTheme() {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    document.documentElement.setAttribute('data-bs-theme', prefersDark ? 'dark' : 'light');
}
setTheme();
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', setTheme);

// Auto-switch to dark mode if the user prefers it
const htmlElement = document.documentElement;
const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
if (prefersDark) {
    htmlElement.setAttribute('data-bs-theme', 'dark');
} else {
    htmlElement.setAttribute('data-bs-theme', 'light');
}