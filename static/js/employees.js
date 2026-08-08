(function () {
    Api.requireAuth();
    renderUserChip();

    const tableBody = document.getElementById('employeeTableBody');
    const emptyState = document.getElementById('emptyState');
    const resultCount = document.getElementById('resultCount');
    const searchInput = document.getElementById('searchInput');
    const departmentFilter = document.getElementById('departmentFilter');
    const statusFilter = document.getElementById('statusFilter');

    const modal = document.getElementById('employeeModal');
    const form = document.getElementById('employeeForm');
    const modalTitle = document.getElementById('modalTitle');

    let allDepartments = new Set();
    let debounceTimer = null;

    function openModal(edit, emp) {
        form.reset();
        document.getElementById('employeeId').value = '';
        document.getElementById('status').value = 'ACTIVE';
        modalTitle.textContent = edit ? 'Edit Employee' : 'Add Employee';

        if (edit && emp) {
            document.getElementById('employeeId').value = emp.id;
            document.getElementById('employeeCode').value = emp.employeeCode || '';
            document.getElementById('firstName').value = emp.firstName || '';
            document.getElementById('lastName').value = emp.lastName || '';
            document.getElementById('email').value = emp.email || '';
            document.getElementById('phone').value = emp.phone || '';
            document.getElementById('department').value = emp.department || '';
            document.getElementById('designation').value = emp.designation || '';
            document.getElementById('dateOfJoining').value = emp.dateOfJoining || '';
            document.getElementById('salary').value = emp.salary != null ? emp.salary : '';
            document.getElementById('status').value = emp.status || 'ACTIVE';
            document.getElementById('address').value = emp.address || '';
        }
        modal.classList.add('open');
    }

    function closeModal() { modal.classList.remove('open'); }

    document.getElementById('addEmployeeBtn').addEventListener('click', () => openModal(false));
    document.getElementById('cancelBtn').addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => { if (e.target === modal) closeModal(); });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = document.getElementById('employeeId').value;
        const payload = {
            employeeCode: document.getElementById('employeeCode').value.trim(),
            firstName: document.getElementById('firstName').value.trim(),
            lastName: document.getElementById('lastName').value.trim(),
            email: document.getElementById('email').value.trim(),
            phone: document.getElementById('phone').value.trim(),
            department: document.getElementById('department').value.trim(),
            designation: document.getElementById('designation').value.trim(),
            dateOfJoining: document.getElementById('dateOfJoining').value,
            salary: document.getElementById('salary').value || 0,
            status: document.getElementById('status').value,
            address: document.getElementById('address').value.trim()
        };

        const saveBtn = document.getElementById('saveEmployeeBtn');
        saveBtn.disabled = true;
        try {
            if (id) {
                await Api.put('api/employees/' + id, payload);
                showToast('Employee updated', 'success');
            } else {
                await Api.post('api/employees', payload);
                showToast('Employee added', 'success');
            }
            closeModal();
            loadEmployees();
        } catch (err) {
            showToast(err.message, 'error');
        } finally {
            saveBtn.disabled = false;
        }
    });

    async function editEmployee(id) {
        try {
            const emp = await Api.get('api/employees/' + id);
            openModal(true, emp);
        } catch (err) {
            showToast(err.message, 'error');
        }
    }

    async function deleteEmployee(id, name) {
        if (!confirm('Delete employee "' + name + '"? This also removes their attendance history.')) return;
        try {
            await Api.del('api/employees/' + id);
            showToast('Employee deleted', 'success');
            loadEmployees();
        } catch (err) {
            showToast(err.message, 'error');
        }
    }

    function statusBadge(status) {
        const cls = status === 'ACTIVE' ? 'badge-active' : 'badge-inactive';
        return '<span class="badge ' + cls + '">' + escapeHtml(status) + '</span>';
    }

    function renderRows(employees) {
        tableBody.innerHTML = '';
        emptyState.style.display = employees.length === 0 ? 'block' : 'none';
        resultCount.textContent = employees.length + ' employee' + (employees.length === 1 ? '' : 's');

        employees.forEach((emp) => {
            const tr = document.createElement('tr');
            const fullName = escapeHtml(emp.firstName) + ' ' + escapeHtml(emp.lastName);
            tr.innerHTML =
                '<td>' + escapeHtml(emp.employeeCode) + '</td>' +
                '<td>' + fullName + '</td>' +
                '<td>' + escapeHtml(emp.email) + '</td>' +
                '<td>' + escapeHtml(emp.department || '-') + '</td>' +
                '<td>' + escapeHtml(emp.designation || '-') + '</td>' +
                '<td>' + escapeHtml(emp.dateOfJoining || '-') + '</td>' +
                '<td>' + statusBadge(emp.status) + '</td>' +
                '<td><div class="row-actions">' +
                    '<button class="btn btn-secondary btn-sm" data-action="edit" data-id="' + emp.id + '">Edit</button>' +
                    '<button class="btn btn-danger btn-sm" data-action="delete" data-id="' + emp.id + '" data-name="' + fullName.replace(/"/g, '&quot;') + '">Delete</button>' +
                '</div></td>';
            tableBody.appendChild(tr);
        });

        tableBody.querySelectorAll('[data-action="edit"]').forEach(btn =>
            btn.addEventListener('click', () => editEmployee(btn.dataset.id)));
        tableBody.querySelectorAll('[data-action="delete"]').forEach(btn =>
            btn.addEventListener('click', () => deleteEmployee(btn.dataset.id, btn.dataset.name)));
    }

    function updateDepartmentOptions(employees) {
        employees.forEach(e => { if (e.department) allDepartments.add(e.department); });
        const current = departmentFilter.value;
        departmentFilter.innerHTML = '<option value="">All Departments</option>' +
            Array.from(allDepartments).sort().map(d => '<option value="' + escapeHtml(d) + '">' + escapeHtml(d) + '</option>').join('');
        departmentFilter.value = current;

        const datalist = document.getElementById('departmentList');
        datalist.innerHTML = Array.from(allDepartments).sort().map(d => '<option value="' + escapeHtml(d) + '">').join('');
    }

    async function loadEmployees() {
        const params = new URLSearchParams();
        if (searchInput.value.trim()) params.set('search', searchInput.value.trim());
        if (departmentFilter.value) params.set('department', departmentFilter.value);
        if (statusFilter.value) params.set('status', statusFilter.value);

        try {
            const employees = await Api.get('api/employees?' + params.toString());
            renderRows(employees);
            updateDepartmentOptions(employees);
        } catch (err) {
            showToast(err.message, 'error');
        }
    }

    searchInput.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(loadEmployees, 300);
    });
    departmentFilter.addEventListener('change', loadEmployees);
    statusFilter.addEventListener('change', loadEmployees);

    loadEmployees();
})();
