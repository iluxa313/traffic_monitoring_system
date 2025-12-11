// Authentication
const API_URL = '/api';

document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch(`${API_URL}/token`, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('token', data.access_token);
            window.location.href = '/index.html';
        } else {
            showError('Неверные учётные данные');
        }
    } catch (error) {
        showError('Ошибка подключения к серверу');
    }
});

function showError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

// Check auth on protected pages
function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token && !window.location.pathname.includes('login')) {
        window.location.href = '/login.html';
    }
}

if (!window.location.pathname.includes('login')) {
    checkAuth();
}
