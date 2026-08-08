(function () {
    Api.requireAuth();
    renderUserChip();

    const tableBody = document.getElementById('attendanceTableBody');
    const emptyState = document.getElementById('emptyState');
    const resultCount = document.getElementById('resultCount');
    const dateInput = document.getElementById('attendanceDate');

    const STATUS_OPTIONS = [
        { value: 'PRESENT', label: 'Present' },
        { value: 'ABSENT', label: 'Absent' },
        { value: 'HALF_DAY', label: 'Half Day' },
        { value: 'LEAVE', label: 'Leave' }
    ];

    function todayIso() {
        const d = new Date();
        return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
    }

    dateInput.value = todayIso();

    function statusSelectHtml(empId, current) {
        return '<select class="status-select" data-emp="' + empId + '">' +
            STATUS_OPTIONS.map(opt =>
                '<option value="' + opt.value + '"' + (opt.value === current ? ' selected' : '') + '>' + opt.label + '</option>'
            ).join('') + '</select>';
    }

    async function loadAttendance() {
        const date = dateInput.value;
        if (!date) return;

        try {
            const [employees, records] = await Promise.all([
                Api.get('api/employees?status=ACTIVE'),
                Api.get('api/attendance?date=' + date)
            ]);

            const recordByEmp = {};
            records.forEach(r => { recordByEmp[r.employeeId] = r; });

            tableBody.innerHTML = '';
            emptyState.style.display = employees.length === 0 ? 'block' : 'none';
            resultCount.textContent = employees.length + ' active employee' + (employees.length === 1 ? '' : 's');

            employees.forEach(emp => {
                const rec = recordByEmp[emp.id];
                const tr = document.createElement('tr');
                tr.dataset.empId = emp.id;
                tr.dataset.attId = rec ? rec.id : '';
                tr.innerHTML =
                    '<td>' + escapeHtml(emp.employeeCode) + '</td>' +
                    '<td>' + escapeHtml(emp.firstName) + ' ' + escapeHtml(emp.lastName) + '</td>' +
                    '<td>' + escapeHtml(emp.department || '-') + '</td>' +
                    '<td>' + statusSelectHtml(emp.id, rec ? rec.status : 'PRESENT') + '</td>' +
                    '<td><input type="time" class="checkin-input" value="' + (rec && rec.checkIn ? rec.checkIn : '') + '"></td>' +
                    '<td><input type="time" class="checkout-input" value="' + (rec && rec.checkOut ? rec.checkOut : '') + '"></td>' +
                    '<td><input type="text" class="remarks-input" placeholder="Optional" value="' + (rec && rec.remarks ? escapeHtml(rec.remarks) : '') + '"></td>' +
                    '<td><button class="btn btn-primary btn-sm save-row-btn">Save</button></td>';
                tableBody.appendChild(tr);
            });

            tableBody.querySelectorAll('.save-row-btn').forEach(btn => {
                btn.addEventListener('click', (e) => saveRow(e.target.closest('tr')));
            });
        } catch (err) {
            showToast(err.message, 'error');
        }
    }

    async function saveRow(tr) {
        const empId = tr.dataset.empId;
        const status = tr.querySelector('.status-select').value;
        const checkIn = tr.querySelector('.checkin-input').value;
        const checkOut = tr.querySelector('.checkout-input').value;
        const remarks = tr.querySelector('.remarks-input').value;
        const btn = tr.querySelector('.save-row-btn');

        btn.disabled = true;
        btn.textContent = 'Saving...';
        try {
            await Api.post('api/attendance', {
                employeeId: Number(empId),
                date: dateInput.value,
                status, checkIn, checkOut, remarks
            });
            showToast('Attendance saved', 'success');
        } catch (err) {
            showToast(err.message, 'error');
        } finally {
            btn.disabled = false;
            btn.textContent = 'Save';
        }
    }

    dateInput.addEventListener('change', loadAttendance);
    loadAttendance();
})();
