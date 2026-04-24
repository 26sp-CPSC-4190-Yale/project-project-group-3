document.addEventListener('DOMContentLoaded', () => {
    async function checkUnreadMessages() {
        try {
            const response = await fetch('/api/unread');
            const data = await response.json();
            
            // Find the Shelf button in the bottom nav on ANY page
            const shelfBtn = document.querySelector('a.nav-btn[href="/profile"]');
            if (!shelfBtn) return;

            let badge = shelfBtn.querySelector('.badge-count');
            
            if (data.count > 0) {
                if (!badge) {
                    badge = document.createElement('span');
                    badge.className = 'badge-count badge-nav';
                    shelfBtn.insertBefore(badge, shelfBtn.querySelector('.nav-dot'));
                }
                badge.textContent = data.count;
            } else if (badge) {
                badge.remove();
            }
        } catch (error) {
            console.error("Background sync failed", error);
        }
    }

    // Run immediately, then check every 3 seconds
    checkUnreadMessages();
    setInterval(checkUnreadMessages, 3000);
});