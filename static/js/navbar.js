/* ═══════════════════════════════════════════════
   USER MENU DROPDOWN
═══════════════════════════════════════════════ */
const userMenu  = document.getElementById('userMenu');
const userBadge = document.getElementById('userBadge');

if (userMenu && userBadge) {
    userBadge.addEventListener('click', (e) => {
        e.stopPropagation();
        // close notif if open
        document.getElementById('notifWrap')?.classList.remove('open');
        const open = userMenu.classList.toggle('open');
        userBadge.setAttribute('aria-expanded', open);
    });

    document.getElementById('userDropdown')?.addEventListener('click', (e) => {
        e.stopPropagation();
    });
}

// close user menu on outside click
document.addEventListener('click', () => {
    userMenu?.classList.remove('open');
    userBadge?.setAttribute('aria-expanded', false);
});


/* ═══════════════════════════════════════════════
   NOTIFICATIONS
═══════════════════════════════════════════════ */
let notifLoaded = false;

// ── Toggle open/close ──
function toggleNotif(e) {
    e.stopPropagation();
    userMenu?.classList.remove('open');
    const wrap   = document.getElementById('notifWrap');
    const isOpen = wrap.classList.toggle('open');
    if (isOpen) {
        notifLoaded = true;
        loadNotifications();
    }
}

// ── Load all notifications ──
async function loadNotifications() {
    const listEl = document.getElementById('notifList');
    if (!listEl) return;

    listEl.innerHTML = '<div class="notif-empty"><span class="spinner"></span></div>';

    try {
        const res   = await fetch('/api/notifications');
        const data  = await res.json();
        const items = data.notifications || [];

        listEl.innerHTML = '';

        if (!items.length) {
            listEl.innerHTML = `
                <div class="notif-empty">
                    <svg width="28" height="28" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M10 2a6 6 0 00-6 6v3l-1.5 2.5h15L16 11V8a6 6 0 00-6-6z"/>
                        <path d="M8 16a2 2 0 004 0"/>
                    </svg>
                    No notifications yet.
                </div>`;
            updateBadge(0);
            return;
        }

        items.forEach(n => listEl.appendChild(buildNotifItem(n)));

        setTimeout(() => updateBadge(0), 400);

    } catch {
        listEl.innerHTML = '<div class="notif-empty">Failed to load.</div>';
    }
}

// ── Build one notification item ──
function buildNotifItem(n) {
    const item = document.createElement('div');
    item.className = `notif-item${n.is_read ? '' : ' unread'}`;
    item.dataset.id = n.id;

    const displayName = n.actor_display_name?.trim() || n.actor_username;
    const time        = timeAgo(n.created_at);

    const messages = {
        follow_request:  `<strong>${displayName}</strong> wants to follow you.`,
        new_follower:    `<strong>${displayName}</strong> started following you.`,
        follow_accepted: `<strong>${displayName}</strong> accepted your follow request.`,
        now_following:   `<strong>${displayName}</strong> is now following you.`,
    };
    const msg = messages[n.type] || `<strong>${displayName}</strong> did something.`;

    const actionsHTML = n.type === 'follow_request' ? `
        <div class="notif-actions" id="notif-actions-${n.id}">
            <button class="notif-action-btn accept" onclick="handleRequest('${n.actor_username}', 'accept', ${n.id})">Accept</button>
            <button class="notif-action-btn reject" onclick="handleRequest('${n.actor_username}', 'reject', ${n.id})">Decline</button>
        </div>` : '';

    const deleteBtn = n.type === 'follow_request' ? '' : `
        <button class="notif-delete" title="Remove" onclick="deleteNotif(${n.id}, this)">
            <svg width="14" height="14" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M5 5l10 10M15 5L5 15"/>
            </svg>
        </button>`;

    item.innerHTML = `
        <a href="/u/${n.actor_username}" class="notif-avatar">${n.actor_username[0].toUpperCase()}</a>
        <div class="notif-content">
            <div class="notif-text">${msg}</div>
            <div class="notif-time">${time}</div>
            ${actionsHTML}
        </div>
        ${deleteBtn}`;

    return item;
}

// ── Accept / Reject follow request ──
async function handleRequest(username, action, notifId) {
    const item = document.querySelector(`.notif-item[data-id="${notifId}"]`);
    if (!item) return;

    item.querySelectorAll('.notif-action-btn').forEach(b => b.disabled = true);

    try {
        const res  = await fetch(`/api/u/${username}/${action}-request`, { method: 'POST' });
        const data = await res.json();

        if (data.success) {
            const actionsEl = document.getElementById(`notif-actions-${notifId}`);
            if (action === 'accept') {
                if (actionsEl) actionsEl.outerHTML = `
                    <div class="notif-followed-label">
                        <svg width="13" height="13" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 10l5 5 7-7"/></svg>
                        Now following you
                    </div>`;
                item.classList.remove('unread');
            } else {
                // reject → remove item
                removeItemAnimated(item);
            }
        } else {
            item.querySelectorAll('.notif-action-btn').forEach(b => b.disabled = false);
        }
    } catch {
        item.querySelectorAll('.notif-action-btn').forEach(b => b.disabled = false);
    }
}

// ── Delete notification ──
async function deleteNotif(notifId, btn) {
    const item = document.querySelector(`.notif-item[data-id="${notifId}"]`);
    if (!item) return;

    btn.disabled = true;

    try {
        const res = await fetch(`/api/notifications/${notifId}`, { method: 'DELETE' });
        if (res.ok) {
            removeItemAnimated(item);
        } else {
            btn.disabled = false;
        }
    } catch {
        btn.disabled = false;
    }
}

// ── Remove item with fade animation ──
function removeItemAnimated(item) {
    item.style.transition = 'opacity 0.25s ease, max-height 0.3s ease, padding 0.3s ease';
    item.style.overflow   = 'hidden';
    item.style.opacity    = '0';
    item.style.maxHeight  = item.offsetHeight + 'px';

    setTimeout(() => {
        item.style.maxHeight = '0';
        item.style.padding   = '0';
        item.style.borderBottom = 'none';
    }, 50);

    setTimeout(() => {
        item.remove();
        const list = document.getElementById('notifList');
        if (list && !list.querySelector('.notif-item')) {
            list.innerHTML = `
                <div class="notif-empty">
                    <svg width="28" height="28" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M10 2a6 6 0 00-6 6v3l-1.5 2.5h15L16 11V8a6 6 0 00-6-6z"/>
                        <path d="M8 16a2 2 0 004 0"/>
                    </svg>
                    No notifications yet.
                </div>`;
        }
    }, 350);
}

// ── Badge ──
function updateBadge(count) {
    const badge = document.getElementById('notifBadge');
    if (!badge) return;
    if (count > 0) {
        badge.textContent = count > 9 ? '9+' : count;
        badge.classList.add('show');
    } else {
        badge.classList.remove('show');
    }
}

// ── Init badge on page load ──
async function initNotifBadge() {
    try {
        const res  = await fetch('/api/notifications/unread-count');
        const data = await res.json();
        updateBadge(data.count || 0);
    } catch {}
}

if (document.getElementById('notifBadge')) {
    initNotifBadge();
}

// ── Close notif on outside click ──
document.addEventListener('click', e => {
    const wrap = document.getElementById('notifWrap');
    if (wrap && !wrap.contains(e.target)) wrap.classList.remove('open');
});

// ── Close on Escape ──
document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
        document.getElementById('notifWrap')?.classList.remove('open');
        userMenu?.classList.remove('open');
        const searchWrap = document.getElementById('searchWrap');
        if (searchWrap) {
            searchWrap.classList.remove('open', 'results');
            const inp = document.getElementById('searchInput');
            if (inp) inp.value = '';
        }
        closeSearchOverlay();
    }
});

// ── Time ago helper ──
function timeAgo(isoString) {
    const diff = Math.floor((Date.now() - new Date(isoString)) / 1000);
    if (diff < 60)       return 'just now';
    if (diff < 3600)     return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400)    return `${Math.floor(diff / 3600)}h ago`;
    if (diff < 2592000)  return `${Math.floor(diff / 86400)}d ago`;
    return `${Math.floor(diff / 2592000)}mo ago`;
}


/* ═══════════════════════════════════════════════
   SEARCH
═══════════════════════════════════════════════ */
let searchDebounceTimer = null;

function toggleSearch(e) {
    e.stopPropagation();

    userMenu?.classList.remove('open');
    document.getElementById('notifWrap')?.classList.remove('open');

    // On mobile open the full-screen overlay instead of expanding inline
    if (window.innerWidth <= 640) {
        const overlay = document.getElementById('searchOverlay');
        if (overlay) {
            overlay.classList.add('open');
            document.body.style.overflow = 'hidden';
            setTimeout(() => document.getElementById('searchOverlayInput')?.focus(), 50);
        }
        return;
    }

    const wrap = document.getElementById('searchWrap');
    if (!wrap) return;

    const isOpen = wrap.classList.toggle('open');
    if (isOpen) {
        setTimeout(() => document.getElementById('searchInput')?.focus(), 50);
    } else {
        wrap.classList.remove('results');
        const inp = document.getElementById('searchInput');
        if (inp) inp.value = '';
    }
}

function closeSearchOverlay() {
    const overlay = document.getElementById('searchOverlay');
    if (!overlay) return;
    overlay.classList.remove('open');
    document.body.style.overflow = '';
    const inp = document.getElementById('searchOverlayInput');
    if (inp) inp.value = '';
    const list = document.getElementById('searchOverlayList');
    if (list) list.innerHTML = '';
}

const searchInputEl = document.getElementById('searchInput');
if (searchInputEl) {
    searchInputEl.addEventListener('input', function () {
        clearTimeout(searchDebounceTimer);
        const q = this.value.trim();
        if (!q) {
            document.getElementById('searchWrap')?.classList.remove('results');
            return;
        }
        searchDebounceTimer = setTimeout(() => fetchSearch(q), 300);
    });

    searchInputEl.addEventListener('click', e => e.stopPropagation());
}

async function fetchSearch(q) {
    const wrap   = document.getElementById('searchWrap');
    const listEl = document.getElementById('searchList');
    if (!wrap || !listEl) return;

    wrap.classList.add('results');
    listEl.innerHTML = '<div class="search-spinner"><span class="spinner"></span></div>';

    try {
        const res   = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
        const data  = await res.json();
        const users = data.users || [];

        listEl.innerHTML = '';

        if (!users.length) {
            listEl.innerHTML = `
                <div class="search-empty">
                    <svg width="28" height="28" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="8.5" cy="8.5" r="5.5"/><path d="M13.5 13.5L18 18"/>
                    </svg>
                    No users found.
                </div>`;
            return;
        }

        users.forEach(u => {
            const a = document.createElement('a');
            a.href = `/u/${u.username}`;
            a.className = 'search-result-item';
            const displayName = u.display_name?.trim() || '';
            a.innerHTML = `
                <div class="search-result-avatar">${u.username[0].toUpperCase()}</div>
                <div class="search-result-info">
                    <div class="search-result-username">@${u.username}</div>
                    ${displayName ? `<div class="search-result-displayname">${displayName}</div>` : ''}
                </div>`;
            listEl.appendChild(a);
        });
    } catch {
        listEl.innerHTML = '<div class="search-empty">Failed to load.</div>';
    }
}

// ── Close search on outside click ──
document.addEventListener('click', e => {
    const wrap = document.getElementById('searchWrap');
    if (wrap && !wrap.contains(e.target)) {
        wrap.classList.remove('open', 'results');
        const inp = document.getElementById('searchInput');
        if (inp) inp.value = '';
    }
});


/* ═══════════════════════════════════════════════
   MOBILE SEARCH OVERLAY
═══════════════════════════════════════════════ */
const searchOverlayInputEl = document.getElementById('searchOverlayInput');
if (searchOverlayInputEl) {
    searchOverlayInputEl.addEventListener('input', function () {
        clearTimeout(searchDebounceTimer);
        const q = this.value.trim();
        const list = document.getElementById('searchOverlayList');
        if (!q) {
            if (list) list.innerHTML = '';
            return;
        }
        searchDebounceTimer = setTimeout(() => fetchSearchOverlay(q), 300);
    });
}

async function fetchSearchOverlay(q) {
    const listEl = document.getElementById('searchOverlayList');
    if (!listEl) return;

    listEl.innerHTML = '<div class="search-spinner"><span class="spinner"></span></div>';

    try {
        const res   = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
        const data  = await res.json();
        const users = data.users || [];

        listEl.innerHTML = '';

        if (!users.length) {
            listEl.innerHTML = `
                <div class="search-empty">
                    <svg width="28" height="28" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="8.5" cy="8.5" r="5.5"/><path d="M13.5 13.5L18 18"/>
                    </svg>
                    No users found.
                </div>`;
            return;
        }

        users.forEach(u => {
            const a = document.createElement('a');
            a.href = `/u/${u.username}`;
            a.className = 'search-result-item';
            const displayName = u.display_name?.trim() || '';
            a.innerHTML = `
                <div class="search-result-avatar">${u.username[0].toUpperCase()}</div>
                <div class="search-result-info">
                    <div class="search-result-username">@${u.username}</div>
                    ${displayName ? `<div class="search-result-displayname">${displayName}</div>` : ''}
                </div>`;
            listEl.appendChild(a);
        });
    } catch {
        listEl.innerHTML = '<div class="search-empty">Failed to load.</div>';
    }
}