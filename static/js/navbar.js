const userMenu   = document.getElementById('userMenu');
    const userBadge  = document.getElementById('userBadge');

    userBadge.addEventListener('click', (e) => {
        e.stopPropagation();
        const open = userMenu.classList.toggle('open');
        userBadge.setAttribute('aria-expanded', open);
    });

    // Close when clicking outside
    document.addEventListener('click', () => {
        userMenu.classList.remove('open');
        userBadge.setAttribute('aria-expanded', false);
    });

    // Prevent dropdown click from closing itself
    document.getElementById('userDropdown').addEventListener('click', (e) => {
        e.stopPropagation();
    });
