// Get CSRF token from meta tag
function getCSRFToken() {
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    if (metaTag) {
        const token = metaTag.getAttribute('content');
        // Validate token length
        if (token && token.length === 64) return token;
        console.warn("CSRF token has invalid length:", token ? token.length : "missing");
    }
    return null;
}

// Generalized romanize function
function romanize(elementId, replace=false) {
    const element = document.getElementById(elementId);
    const csrftoken = getCSRFToken();

    if (!csrftoken) {
        console.error("CSRF token not found");
        return Promise.reject(new Error("Security token missing"));
    }

    return fetch('/ytm/romanize/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrftoken
        },
        body: `lyrics=${encodeURIComponent(element.value)}`,
        credentials: 'include'  // Required for session cookies
    })
        .then(response => {
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return response.json();
        })
        .then(data => {
            if (data.romanized) {
                if (replace) element.value = data.romanized;
                return data.romanized;
            }
            throw new Error(data.error || 'Romanization failed');
        });
}

function append_romanization(elementId, button) {
    const element = document.getElementById(elementId);
    if (!element) return;

    // Handle button loading state
    let originalText;
    if (button) {
        originalText = button.innerHTML;
        button.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
        button.disabled = true;
    }

    romanize(elementId)
        .then(romanized => {
            const currentValue = element.value.trim();
            const separator = currentValue ? ' / ' : '';
            element.value = currentValue + separator + romanized;
        })
        .catch(error => {
            alert('Error: ' + error.message);
        })
        .finally(() => {
            if (button) {
                button.innerHTML = originalText;
                button.disabled = false;
            }
        });
}
