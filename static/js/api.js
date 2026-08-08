/* Shared API helper: token storage, fetch wrapper, toast, and auth guard. */

const Api = (() => {
    const TOKEN_KEY = 'ems_token';
    const USER_KEY = 'ems_user';

    function getToken() { return localStorage.getItem(TOKEN_KEY); }
    function getUser() {
        const raw = localStorage.getItem(USER_KEY);
        return raw ? JSON.parse(raw) : null;
    }
    function setSession(token, user) {
        localStorage.setItem(TOKEN_KEY, token);
        localStorage.setItem(USER_KEY, JSON.stringify(user));
    }
    function clearSession() {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
    }

    async function request(path, options = {}) {
        const headers = Object.assign({ 'Content-Type': 'application/json' }, options.headers || {});
        const token = getToken();
        if (token) headers['Authorization'] = 'Bearer ' + token;

        const res = await fetch(path, Object.assign({}, options, { headers }));

        if (res.status === 401) {
            clearSession();
            if (!location.pathname.endsWith('index.html') && location.pathname !== '/') {
                window.location.href = 'index.html';
            }
            throw new Error('Session expired. Please log in again.');
        }

        let data = null;
        try { data = await res.json(); } catch (e) { /* no body */ }

        if (!res.ok) {
            const msg = (data && data.error) ? data.error : ('Request failed (' + res.status + ')');
            throw new Error(msg);
        }
        return data;
    }

    function get(path) { return request(path, { method: 'GET' }); }
    function post(path, body) { return request(path, { method: 'POST', body: JSON.stringify(body) }); }
    function put(path, body) { return request(path, { method: 'PUT', body: JSON.stringify(body) }); }
    function del(path) { return request(path, { method: 'DELETE' }); }

    /** Redirects to login if not authenticated. Call at top of protected pages. */
    function requireAuth() {
        if (!getToken()) {
            window.location.href = 'index.html';
        }
    }

    return { getToken, getUser, setSession, clearSession, get, post, put, del, requireAuth };
})();

function showToast(message, type = 'info') {
    const el = document.getElementById('toast');
    if (!el) return;
    el.textContent = message;
    el.className = 'show' + (type === 'error' ? ' error' : type === 'success' ? ' success' : '');
    clearTimeout(showToast._t);
    showToast._t = setTimeout(() => { el.className = ''; }, 3200);
}

function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

async function logout() {
    try { await Api.post('api/logout', {}); } catch (e) { /* ignore */ }
    Api.clearSession();
    window.location.href = 'index.html';
}

function renderUserChip() {
    const user = Api.getUser();
    const nameEl = document.getElementById('sidebarUserName');
    const roleEl = document.getElementById('sidebarUserRole');
    if (user && nameEl) nameEl.textContent = user.fullName || user.username;
    if (user && roleEl) roleEl.textContent = user.role || '';
}
