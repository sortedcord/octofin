// Generalized romanize function
function romanize(elementId, replace=false) {
    const element = document.getElementById(elementId);
    return fetch('/ytm/romanize/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': '{{ csrf_token }}'
        },
        body: `lyrics=${encodeURIComponent(element.value)}`
    })
        .then(response => response.json())
        .then(data => {
            if (data.romanized) {
                if (replace) {
                    element.value = data.romanized;
                }
                return data.romanized;
            } else {
                throw new Error(data.error || 'Unknown error');
            }
        });
}

function append_romanization(elementId, button) {
    const element = document.getElementById(elementId);
    if (!element) return;

    // Optional: handle button loading state
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