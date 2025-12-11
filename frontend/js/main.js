const API_URL = '/api';

function getToken() {
    return localStorage.getItem('token');
}

async function fetchAPI(endpoint, options = {}) {
    const token = getToken();
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers
    });

    if (response.status === 401) {
        localStorage.removeItem('token');
        window.location.href = '/login.html';
        return;
    }

    return response.json();
}

// Navigation
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const page = e.target.dataset.page;

        if (page) {
            // Hide all pages
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            // Show selected page
            document.getElementById(`${page}-page`).classList.add('active');

            // Update active link
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            e.target.classList.add('active');

            // Load page data
            loadPageData(page);
        }
    });
});

// Logout
document.getElementById('logoutBtn')?.addEventListener('click', (e) => {
    e.preventDefault();
    localStorage.removeItem('token');
    window.location.href = '/login.html';
});

// Load dashboard on startup
async function loadDashboard() {
    try {
        const status = await fetchAPI('/status');
        document.getElementById('activeIncidents').textContent = status.active_incidents;
        document.getElementById('criticalEvents').textContent = status.critical_events;
        document.getElementById('networkLoad').textContent = `${Math.round(status.network_load)}%`;

        // Load top traffic
        const traffic = await fetchAPI('/traffic/top');
        const tbody = document.querySelector('#topTrafficTable tbody');

        if (traffic && traffic.length > 0) {
            tbody.innerHTML = traffic.map(t => `
                <tr>
                    <td>${t.srcIP}</td>
                    <td>${t.dstIP}</td>
                    <td>${(t.bytes / 1024 / 1024).toFixed(2)}</td>
                </tr>
            `).join('');
        } else {
            tbody.innerHTML = '<tr><td colspan="3">Нет данных</td></tr>';
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

function loadPageData(page) {
    switch(page) {
        case 'main':
            loadDashboard();
            break;
        case 'incidents':
            loadIncidents();
            break;
        case 'rules':
            loadRules();
            break;
        case 'monitoring':
            refreshMonitoring();
            break;
    }
}

function navigateToIncidents() {
    document.querySelector('.nav-link[data-page="incidents"]').click();
}

function openMonitoring() {
    document.querySelector('.nav-link[data-page="monitoring"]').click();
}

// Initialize
if (window.location.pathname.includes('index.html') || window.location.pathname === '/') {
    loadDashboard();
}
