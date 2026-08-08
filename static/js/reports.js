(function () {
    Api.requireAuth();
    renderUserChip();

    const tableBody = document.getElementById('reportTableBody');
    const emptyState = document.getElementById('emptyState');
    const resultCount = document.getElementById('resultCount');
    const monthSelect = document.getElementById('monthSelect');
    const yearSelect = document.getElementById('yearSelect');

    const MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December'];

    function populateSelectors() {
        const now = new Date();
        monthSelect.innerHTML = MONTHS.map((m, i) =>
            '<option value="' + (i + 1) + '"' + (i + 1 === now.getMonth() + 1 ? ' selected' : '') + '>' + m + '</option>'
        ).join('');

        const years = [];
        for (let y = now.getFullYear() - 3; y <= now.getFullYear() + 1; y++) years.push(y);
        yearSelect.innerHTML = years.map(y =>
            '<option value="' + y + '"' + (y === now.getFullYear() ? ' selected' : '') + '>' + y + '</option>'
        ).join('');
    }

    async function loadReport() {
        const month = monthSelect.value;
        const year = yearSelect.value;
        try {
            const rows = await Api.get('api/attendance/summary?month=' + month + '&year=' + year);
            tableBody.innerHTML = '';
            emptyState.style.display = rows.length === 0 ? 'block' : 'none';
            resultCount.textContent = rows.length + ' employee' + (rows.length === 1 ? '' : 's');

            rows.forEach(r => {
                const total = r.present + r.absent + r.halfDay + r.leave;
                const tr = document.createElement('tr');
                tr.innerHTML =
                    '<td>' + escapeHtml(r.employeeCode) + '</td>' +
                    '<td>' + escapeHtml(r.employeeName) + '</td>' +
                    '<td><span class="badge badge-present">' + r.present + '</span></td>' +
                    '<td><span class="badge badge-absent">' + r.absent + '</span></td>' +
                    '<td><span class="badge badge-half">' + r.halfDay + '</span></td>' +
                    '<td><span class="badge badge-leave">' + r.leave + '</span></td>' +
                    '<td>' + total + '</td>';
                tableBody.appendChild(tr);
            });
        } catch (err) {
            showToast(err.message, 'error');
        }
    }

    monthSelect.addEventListener('change', loadReport);
    yearSelect.addEventListener('change', loadReport);

    populateSelectors();
    loadReport();
})();
