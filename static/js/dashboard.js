(function () {
    Api.requireAuth();
    renderUserChip();

    async function load() {
        try {
            const stats = await Api.get('api/dashboard/stats');
            document.getElementById('statTotal').textContent = stats.totalEmployees;
            document.getElementById('statActive').textContent = stats.activeEmployees;
            document.getElementById('statPresent').textContent = stats.presentToday;
            document.getElementById('statAbsent').textContent = stats.absentToday;
            document.getElementById('statLeave').textContent = stats.onLeaveToday;
            document.getElementById('statDept').textContent = stats.departments;
        } catch (err) {
            showToast(err.message, 'error');
        }
    }

    load();
})();
