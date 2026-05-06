document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('search-form');
    const resultsContainer = document.getElementById('results-container');
    const countDisplay = document.getElementById('count-display');

    if (!form || !resultsContainer) return; 

    let debounceTimer = null;
    function scheduleFetch() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(fetchResults, 300);
    }

    async function fetchResults() {
        const params = new URLSearchParams(new FormData(form));
        try {
            const response = await fetch(`/api/search?${params.toString()}`);
            if (response.ok) {
                const html = await response.text();
                resultsContainer.innerHTML = html;
                updateCount();
            }
        } catch (error) {
            console.error("Error fetching results", error);
        }
    }

    function updateCount() {
        const count = resultsContainer.querySelectorAll('.result-card').length;
        countDisplay.textContent = `${count} listing${count === 1 ? '' : 's'} found`;
    }

    // ─── Event delegation ───
    resultsContainer.addEventListener('submit', async function(event) {
        const targetForm = event.target;

        if (targetForm.matches('.save-form') || targetForm.matches('.unsave-form')) {
            event.preventDefault();
            await handleToggleSave(targetForm);
        }

        if (targetForm.matches('.delete-form')) {
            event.preventDefault();
            await handleDelete(targetForm);
        }
    });

    async function handleToggleSave(formElement) {
        const btn = formElement.querySelector('button');
        const isSaved = formElement.matches('.unsave-form');
        const actionUrl = formElement.getAttribute('action');

        // Optimistic UI update
        btn.classList.toggle('saved-active', !isSaved);
        btn.innerHTML = isSaved ? '♡' : '♥';

        // Flip the form's class and action for the next click
        if (isSaved) {
            formElement.classList.replace('unsave-form', 'save-form');
            formElement.setAttribute('action', actionUrl.replace('/unsave/', '/save/'));
        } else {
            formElement.classList.replace('save-form', 'unsave-form');
            formElement.setAttribute('action', actionUrl.replace('/save/', '/unsave/'));
        }

        try {
            const response = await fetch(actionUrl, {
                method: 'POST',
                headers: { 'Accept': 'application/json' },
                credentials: 'same-origin'
            });

            if (!response.ok) {
                // Rollback on failure
                btn.classList.toggle('saved-active', isSaved);
                btn.innerHTML = isSaved ? '♥' : '♡';
                if (isSaved) {
                    formElement.classList.replace('save-form', 'unsave-form');
                    formElement.setAttribute('action', actionUrl);
                } else {
                    formElement.classList.replace('unsave-form', 'save-form');
                    formElement.setAttribute('action', actionUrl);
                }
            }
        } catch (error) {
            console.error("Failed to save/unsave listing", error);
        }
    }

    async function handleDelete(formElement) {
        if (!confirm("Permanently delete this listing?")) return;

        const actionUrl = formElement.getAttribute('action');
        const card = formElement.closest('.result-card');
        if (card) card.style.display = 'none';

        try {
            const response = await fetch(actionUrl, {
                method: 'POST',
                headers: { 'Accept': 'application/json' },
                credentials: 'same-origin'
            });

            if (!response.ok) {
                if (card) card.style.display = 'flex';
                console.error('Delete failed with status:', response.status);
                return;
            }

            updateCount();
        } catch (error) {
            console.error('Failed to delete listing:', error);
            if (card) card.style.display = 'flex';
        }
    }

    // ─── Search form listeners ───
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        fetchResults();
    });

    form.addEventListener('change', fetchResults); 
    form.addEventListener('input', function(e) {
        if (e.target.id === 'search-input') {
            scheduleFetch();
        } else {
            fetchResults(); 
        }
    });

    // Initial load
    fetchResults();
});