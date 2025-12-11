// Chart visualization (placeholder - would use Chart.js in production)
function initCharts() {
    // Network chart
    const networkCanvas = document.getElementById('networkChart');
    if (networkCanvas) {
        const ctx = networkCanvas.getContext('2d');
        ctx.fillStyle = '#3498db';
        ctx.fillRect(0, 0, networkCanvas.width, networkCanvas.height);
        ctx.fillStyle = '#fff';
        ctx.font = '20px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('График загрузки сети', networkCanvas.width/2, networkCanvas.height/2);
    }

    // Packets chart
    const packetsCanvas = document.getElementById('packetsChart');
    if (packetsCanvas) {
        const ctx = packetsCanvas.getContext('2d');
        ctx.fillStyle = '#2ecc71';
        ctx.fillRect(0, 0, packetsCanvas.width, packetsCanvas.height);
        ctx.fillStyle = '#fff';
        ctx.font = '20px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('График пакетов', packetsCanvas.width/2, packetsCanvas.height/2);
    }
}

async function loadRules() {
    try {
        const rules = await fetchAPI('/rules');
        const tbody = document.getElementById('rulesTable');

        if (rules && rules.length > 0) {
            tbody.innerHTML = rules.map(rule => `
                <tr>
                    <td>${rule.id}</td>
                    <td>${rule.name}</td>
                    <td>${rule.srcIP || '*'}</td>
                    <td>${rule.dstIP || '*'}</td>
                    <td>*</td>
                    <td><span class="badge ${rule.action === 'DROP' ? 'badge-danger' : 'badge-info'}">${rule.action}</span></td>
                    <td>${rule.expiration ? new Date(rule.expiration).toLocaleString('ru-RU') : 'Нет'}</td>
                    <td><span class="badge badge-warning">${rule.type === 'auto' ? 'Авто' : 'Ручное'}</span></td>
                    <td>
                        <button class="btn btn-secondary" onclick="editRule(${rule.id})">Редактировать</button>
                        <button class="btn btn-danger" onclick="deleteRule(${rule.id})">Удалить</button>
                    </td>
                </tr>
            `).join('');
        } else {
            tbody.innerHTML = '<tr><td colspan="9">Нет правил</td></tr>';
        }
    } catch (error) {
        console.error('Error loading rules:', error);
    }
}

function openRuleModal() {
    alert('Создание правила (в продакшн версии открывается модальное окно)');
}

function editRule(id) {
    alert(`Редактирование правила #${id}`);
}

function deleteRule(id) {
    if (confirm(`Удалить правило #${id}?`)) {
        alert(`Правило #${id} удалено`);
    }
}

function generateReport() {
    alert('Генерация отчёта...');
}

function exportPDF() {
    alert('Экспорт в PDF...');
}

function saveSettings() {
    alert('Настройки сохранены');
}

function resetSettings() {
    alert('Настройки сброшены');
}

// Initialize charts when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCharts);
} else {
    initCharts();
}
