// ── User menu dropdown ────────────────────────────────────────
const userMenu  = document.getElementById('userMenu');
const userBadge = document.getElementById('userBadge');

if (userMenu && userBadge) {
    userBadge.addEventListener('click', (e) => {
        e.stopPropagation();
        const open = userMenu.classList.toggle('open');
        userBadge.setAttribute('aria-expanded', open);
    });

    document.addEventListener('click', () => {
        userMenu.classList.remove('open');
        userBadge.setAttribute('aria-expanded', false);
    });

    document.getElementById('userDropdown').addEventListener('click', (e) => {
        e.stopPropagation();
    });
}

// ── Notifications ─────────────────────────────────────────────
let notifLoaded = false;

function toggleNotif(e) {
    e.stopPropagation();
    const wrap = document.getElementById('notifWrap');
    if (!wrap) return;
    const isOpen = wrap.classList.toggle('open');
    if (isOpen && !notifLoaded) { notifLoaded = true; loadNotifications(); }
}

async function loadNotifications() {
    const listEl = document.getElementById('notifList');
    if (!listEl) return;
    try {
        const res      = await fetch('/api/me/pending-requests');
        const data     = await res.json();
        const requests = data.users || [];
        listEl.innerHTML = '';
        if (!requests.length) {
            listEl.innerHTML = '<div class="notif-empty">No notifications.</div>';
            return;
        }
        requests.forEach(r => listEl.appendChild(buildRequestItem(r)));
        updateBadge(requests.length);
    } catch {
        listEl.innerHTML = '<div class="notif-empty">Failed to load.</div>';
    }
}

function timeAgo(isoString) {
    const diff = Math.floor((Date.now() - new Date(isoString)) / 1000);
    if (diff < 60)         return 'just now';
    if (diff < 3600)       return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400)      return `${Math.floor(diff / 3600)}h ago`;
    if (diff < 2592000)    return `${Math.floor(diff / 86400)}d ago`;
    return `${Math.floor(diff / 2592000)}mo ago`;
}

function buildRequestItem(r) {
    const item = document.createElement('div');
    item.className = 'notif-item';
    item.dataset.username = r.username;
    item.innerHTML = `
        <div class="notif-item-top">
            <a href="/u/${r.username}" class="notif-avatar">${r.username[0].toUpperCase()}</a>
            <div class="notif-text">
                <strong>${r.display_name?.trim() || r.username}</strong>
                <span class="notif-sub"> requested to follow you.</span>
                <div style="font-size:11.5px;color:var(--ink-muted);margin-top:2px;">${timeAgo(r.created_at)}</div>
            </div>
        </div>
        <div class="notif-actions">
            <button class="notif-action-btn accept" onclick="handleRequest('${r.username}', 'accept', this)">Accept</button>
            <button class="notif-action-btn reject" onclick="handleRequest('${r.username}', 'reject', this)">Decline</button>
        </div>`;
    return item;
}

// ── Auto-check badge on page load ─────────────────────────────
async function initNotifBadge() {
    try {
        const res  = await fetch('/api/me/pending-requests');
        const data = await res.json();
        const count = (data.users || []).length;
        updateBadge(count);
    } catch {}
}

// run on load if user is logged in
if (document.getElementById('notifBadge')) {
    initNotifBadge();
}

async function handleRequest(username, action) {
    const item = document.querySelector(`.notif-item[data-username="${username}"]`);
    if (!item) return;
    item.querySelectorAll('.notif-action-btn').forEach(b => b.disabled = true);
    try {
        const res  = await fetch(`/api/u/${username}/${action}-request`, { method: 'POST' });
        const data = await res.json();
        if (data.success) {
            if (action === 'accept') {
                item.querySelector('.notif-actions').outerHTML = `
                    <div class="notif-followed-label">
                        <svg width="13" height="13" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 10l5 5 7-7"/></svg>
                        Follow request accepted
                    </div>`;
            } else {
                item.style.transition = 'opacity 0.3s ease';
                item.style.opacity = '0';
                setTimeout(() => {
                    item.remove();
                    const list = document.getElementById('notifList');
                    if (list && !list.querySelector('.notif-item')) {
                        list.innerHTML = '<div class="notif-empty">No notifications.</div>';
                        updateBadge(0);
                    } else {
                        updateBadge(document.querySelectorAll('.notif-item').length);
                    }
                }, 300);
            }
            const pending = document.querySelectorAll('.notif-item .notif-action-btn').length / 2;
            updateBadge(Math.max(0, pending - (action === 'reject' ? 1 : 0)));
        } else {
            item.querySelectorAll('.notif-action-btn').forEach(b => b.disabled = false);
        }
    } catch {
        item.querySelectorAll('.notif-action-btn').forEach(b => b.disabled = false);
    }
}

function updateBadge(count) {
    const badge = document.getElementById('notifBadge');
    if (!badge) return;
    if (count > 0) { badge.textContent = count > 9 ? '9+' : count; badge.classList.add('show'); }
    else { badge.classList.remove('show'); }
}

document.addEventListener('click', e => {
    const wrap = document.getElementById('notifWrap');
    if (wrap && !wrap.contains(e.target)) wrap.classList.remove('open');
});

document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
        document.getElementById('notifWrap')?.classList.remove('open');
    }
});