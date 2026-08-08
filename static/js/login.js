(function () {
    // Already logged in? Skip straight to the dashboard.
    if (Api.getToken()) {
        window.location.href = 'dashboard.html';
        return;
    }

    const form = document.getElementById('loginForm');
    const errorBox = document.getElementById('loginError');
    const btn = document.getElementById('loginBtn');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        errorBox.classList.remove('show');
        btn.disabled = true;
        btn.textContent = 'Signing in...';

        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;

        try {
            const data = await Api.post('api/login', { username, password });
            Api.setSession(data.token, {
                username: data.username,
                fullName: data.fullName,
                role: data.role
            });
            window.location.href = 'dashboard.html';
        } catch (err) {
            errorBox.textContent = err.message || 'Login failed. Please try again.';
            errorBox.classList.add('show');
            btn.disabled = false;
            btn.textContent = 'Sign In';
        }
    });
})();
