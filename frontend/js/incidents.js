async function loadIncidents() {
    try {
        const incidents = await fetchAPI('/incidents');
        const tbody = document.getElementById('incidentsTable');

        if (incidents && incidents.length > 0) {
            tbody.innerHTML = incidents.map(inc => {
                const severityBadge = inc.severity >= 3 ? 'badge-critical' : 
                                     inc.severity === 2 ? 'badge-warning' : 'badge-info';
                const statusBadge = inc.status === 'Closed' ? 'badge-success' :
                                   inc.status === 'Mitigated' ? 'badge-info' : 'badge-warning';

                return `
                    <tr>
                        <td>${inc.id}</td>
                        <td>${new Date(inc.time).toLocaleString('ru-RU')}</td>
                        <td>${inc.type}</td>
                        <td>${inc.srcIP}</td>
                        <td><span class="badge ${severityBadge}">${inc.severity === 3 ? 'Critical' : inc.severity === 2 ? 'Warning' : 'Info'}</span></td>
                        <td><span class="badge ${statusBadge}">${inc.status}</span></td>
                        <td>
                            <button class="btn btn-primary" onclick="openIncident(${inc.id})">Открыть</button>
                            ${inc.status !== 'Closed' ? `<button class="btn btn-success" onclick="closeIncident(${inc.id})">Закрыть</button>` : ''}
                        </td>
                    </tr>
                `;
            }).join('');
        } else {
            tbody.innerHTML = '<tr><td colspan="7">Нет инцидентов</td></tr>';
        }
    } catch (error) {
        console.error('Error loading incidents:', error);
        document.getElementById('incidentsTable').innerHTML = 
            '<tr><td colspan="7">Ошибка загрузки данных</td></tr>';
    }
}

function openIncident(id) {
    alert(`Открытие инцидента #${id}`);
    // Here you would open a modal with incident details
}

async function closeIncident(id) {
    if (confirm(`Закрыть инцидент #${id}?`)) {
        try {
            await fetchAPI(`/incidents/${id}/close`, { method: 'POST' });
            loadIncidents(); // Reload
            alert('Инцидент закрыт');
        } catch (error) {
            alert('Ошибка при закрытии инцидента');
        }
    }
}
