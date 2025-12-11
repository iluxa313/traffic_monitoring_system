async function refreshMonitoring() {
    console.log('Refreshing monitoring data...');
    // In a real system, this would fetch live data
    document.getElementById('activeFlows').innerHTML = 
        '<tr><td colspan="6">Обновление данных...</td></tr>';

    setTimeout(() => {
        document.getElementById('activeFlows').innerHTML = `
            <tr>
                <td>10.0.0.10</td>
                <td>10.0.1.5</td>
                <td>52310 → 443</td>
                <td>TCP</td>
                <td>250</td>
                <td><button class="btn btn-danger" onclick="blockFlow('10.0.0.10')">Блокировать</button></td>
            </tr>
        `;
    }, 1000);
}

async function startCapture() {
    if (confirm('Начать захват трафика? Это может занять некоторое время.')) {
        try {
            const result = await fetchAPI('/capture/start', { method: 'POST' });
            alert(`Захвачено пакетов: ${result.captured}\nОбработано событий: ${result.processed}\nИнцидентов: ${result.incidents}`);
            refreshMonitoring();
        } catch (error) {
            alert('Ошибка при захвате трафика');
        }
    }
}

function blockFlow(ip) {
    if (confirm(`Заблокировать IP ${ip}?`)) {
        alert(`IP ${ip} заблокирован`);
    }
}
