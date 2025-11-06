// 전역 변수
let updateInterval = null;
let monitoringInterval = null;
let isMonitoring = false;
let monitoringStartTime = null;
let monitoringDuration = 300; // 5분 (초)

// Chart.js 차트 객체
let cpuChart, memoryChart, networkChart, comparisonChart;

// 차트 데이터
let chartData = {
    labels: [],
    cpu: [],
    memory: [],
    networkSent: [],
    networkRecv: [],
    gpu: []
};

const MAX_DATA_POINTS = 50;

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    startRealtimeUpdates();
    setupEventListeners();
});

// 차트 초기화
function initializeCharts() {
    // CPU 차트
    const cpuCtx = document.getElementById('cpuChart').getContext('2d');
    cpuChart = new Chart(cpuCtx, {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: 'CPU Usage (%)',
                data: chartData.cpu,
                borderColor: 'rgb(102, 126, 234)',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            },
            animation: {
                duration: 750
            }
        }
    });

    // 메모리 차트
    const memoryCtx = document.getElementById('memoryChart').getContext('2d');
    memoryChart = new Chart(memoryCtx, {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: 'Memory Usage (%)',
                data: chartData.memory,
                borderColor: 'rgb(245, 87, 108)',
                backgroundColor: 'rgba(245, 87, 108, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            },
            animation: {
                duration: 750
            }
        }
    });

    // 네트워크 차트
    const networkCtx = document.getElementById('networkChart').getContext('2d');
    networkChart = new Chart(networkCtx, {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: [
                {
                    label: 'Sent (MB)',
                    data: chartData.networkSent,
                    borderColor: 'rgb(67, 233, 123)',
                    backgroundColor: 'rgba(67, 233, 123, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'Received (MB)',
                    data: chartData.networkRecv,
                    borderColor: 'rgb(56, 249, 215)',
                    backgroundColor: 'rgba(56, 249, 215, 0.1)',
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            animation: {
                duration: 750
            }
        }
    });

    // 비교 차트
    const comparisonCtx = document.getElementById('comparisonChart').getContext('2d');
    comparisonChart = new Chart(comparisonCtx, {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: [
                {
                    label: 'CPU (%)',
                    data: chartData.cpu,
                    borderColor: 'rgb(102, 126, 234)',
                    tension: 0.4
                },
                {
                    label: 'Memory (%)',
                    data: chartData.memory,
                    borderColor: 'rgb(245, 87, 108)',
                    tension: 0.4
                },
                {
                    label: 'GPU (%)',
                    data: chartData.gpu,
                    borderColor: 'rgb(250, 112, 154)',
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            },
            animation: {
                duration: 750
            }
        }
    });
}

// 이벤트 리스너 설정
function setupEventListeners() {
    document.getElementById('startBtn').addEventListener('click', startMonitoring);
    document.getElementById('stopBtn').addEventListener('click', stopMonitoring);
    document.getElementById('downloadBtn').addEventListener('click', downloadPDF);
}

// 실시간 업데이트 시작
function startRealtimeUpdates() {
    updateData();
    updateInterval = setInterval(updateData, 2000); // 2초마다 업데이트
}

// 데이터 업데이트
async function updateData() {
    try {
        const response = await fetch('/api/current');
        const result = await response.json();

        if (result.success) {
            const data = result.data;
            updateUI(data);
            updateCharts(data);
        }
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

// UI 업데이트
function updateUI(data) {
    // CPU
    const cpuUsage = data.cpu.usage_total.toFixed(1);
    document.getElementById('cpuValue').textContent = `${cpuUsage}%`;
    document.getElementById('cpuDetail').textContent =
        `${data.cpu.core_count} cores, ${data.cpu.thread_count} threads`;

    // Memory
    const memUsage = data.memory.virtual.percent.toFixed(1);
    document.getElementById('memoryValue').textContent = `${memUsage}%`;
    document.getElementById('memoryDetail').textContent =
        `${data.memory.virtual.used_gb} GB / ${data.memory.virtual.total_gb} GB`;

    // Disk
    if (data.disk.partitions.length > 0) {
        const diskUsage = data.disk.partitions[0].percent.toFixed(1);
        document.getElementById('diskValue').textContent = `${diskUsage}%`;
        document.getElementById('diskDetail').textContent =
            `${data.disk.partitions[0].used_gb} GB / ${data.disk.partitions[0].total_gb} GB`;
    }

    // Network
    document.getElementById('networkValue').textContent =
        `${data.network.sent_mb.toFixed(2)} MB`;
    document.getElementById('networkDetail').textContent =
        `↑ ${data.network.sent_mb.toFixed(2)} MB | ↓ ${data.network.recv_mb.toFixed(2)} MB`;

    // GPU
    if (Array.isArray(data.gpu) && data.gpu.length > 0) {
        document.getElementById('gpuValue').textContent = `${data.gpu[0].load.toFixed(1)}%`;
        document.getElementById('gpuDetail').textContent =
            `${data.gpu[0].name} - ${data.gpu[0].memory_used} MB / ${data.gpu[0].memory_total} MB`;
    } else {
        document.getElementById('gpuValue').textContent = 'N/A';
        document.getElementById('gpuDetail').textContent = 'No GPU detected';
    }

    // Temperature
    if (data.temperature && !data.temperature.error && !data.temperature.info) {
        const firstSensor = Object.values(data.temperature)[0];
        if (firstSensor && firstSensor.length > 0) {
            document.getElementById('tempValue').textContent =
                `${firstSensor[0].current.toFixed(1)}°C`;
            document.getElementById('tempDetail').textContent =
                `${firstSensor[0].label || 'Sensor'}`;
        } else {
            document.getElementById('tempValue').textContent = 'N/A';
            document.getElementById('tempDetail').textContent = 'No sensors';
        }
    } else {
        document.getElementById('tempValue').textContent = 'N/A';
        document.getElementById('tempDetail').textContent = 'Not available';
    }

    // 상세 정보
    updateDetailedInfo(data);

    // 프로세스 테이블
    updateProcessTable(data.top_processes);
}

// 상세 정보 업데이트
function updateDetailedInfo(data) {
    // CPU 정보
    document.getElementById('cpuInfo').innerHTML = `
        <strong>Total Usage:</strong> ${data.cpu.usage_total.toFixed(1)}%<br>
        <strong>Cores:</strong> ${data.cpu.core_count}<br>
        <strong>Threads:</strong> ${data.cpu.thread_count}<br>
        <strong>Frequency:</strong> ${data.cpu.frequency.current.toFixed(0)} MHz
    `;

    // 메모리 정보
    document.getElementById('memoryInfo').innerHTML = `
        <strong>Used:</strong> ${data.memory.virtual.used_gb} GB<br>
        <strong>Available:</strong> ${data.memory.virtual.available_gb} GB<br>
        <strong>Total:</strong> ${data.memory.virtual.total_gb} GB<br>
        <strong>Swap:</strong> ${data.memory.swap.used_gb} GB / ${data.memory.swap.total_gb} GB
    `;

    // 디스크 정보
    let diskHTML = '';
    data.disk.partitions.forEach(partition => {
        diskHTML += `
            <strong>${partition.mountpoint}:</strong><br>
            Used: ${partition.used_gb} GB / ${partition.total_gb} GB (${partition.percent.toFixed(1)}%)<br>
        `;
    });
    document.getElementById('diskInfo').innerHTML = diskHTML;

    // 네트워크 정보
    document.getElementById('networkInfo').innerHTML = `
        <strong>Sent:</strong> ${data.network.sent_mb.toFixed(2)} MB<br>
        <strong>Received:</strong> ${data.network.recv_mb.toFixed(2)} MB<br>
        <strong>Connections:</strong> ${data.network.connections}<br>
        <strong>Interfaces:</strong> ${data.network.interfaces.length}
    `;
}

// 프로세스 테이블 업데이트
function updateProcessTable(processes) {
    const tbody = document.getElementById('processTableBody');
    tbody.innerHTML = '';

    processes.forEach(proc => {
        const row = tbody.insertRow();
        row.innerHTML = `
            <td>${proc.pid}</td>
            <td>${proc.name}</td>
            <td>${(proc.cpu_percent || 0).toFixed(1)}%</td>
            <td>${(proc.memory_percent || 0).toFixed(1)}%</td>
            <td>${proc.status}</td>
        `;
    });
}

// 차트 업데이트
function updateCharts(data) {
    const now = new Date().toLocaleTimeString();

    // 데이터 추가
    chartData.labels.push(now);
    chartData.cpu.push(data.cpu.usage_total);
    chartData.memory.push(data.memory.virtual.percent);
    chartData.networkSent.push(data.network.sent_mb);
    chartData.networkRecv.push(data.network.recv_mb);

    if (Array.isArray(data.gpu) && data.gpu.length > 0) {
        chartData.gpu.push(data.gpu[0].load);
    } else {
        chartData.gpu.push(0);
    }

    // 최대 데이터 포인트 제한
    if (chartData.labels.length > MAX_DATA_POINTS) {
        chartData.labels.shift();
        chartData.cpu.shift();
        chartData.memory.shift();
        chartData.networkSent.shift();
        chartData.networkRecv.shift();
        chartData.gpu.shift();
    }

    // 차트 업데이트
    cpuChart.update('none');
    memoryChart.update('none');
    networkChart.update('none');
    comparisonChart.update('none');
}

// 5분 모니터링 시작
async function startMonitoring() {
    try {
        const response = await fetch('/api/start-monitoring', {
            method: 'POST'
        });
        const result = await response.json();

        if (result.success) {
            isMonitoring = true;
            monitoringStartTime = Date.now();

            document.getElementById('startBtn').disabled = true;
            document.getElementById('stopBtn').disabled = false;
            document.getElementById('downloadBtn').disabled = true;
            document.getElementById('statusText').textContent = 'Monitoring Active (5:00)';
            document.getElementById('statusText').classList.add('monitoring-active');

            // 프로그레스 바 표시
            document.getElementById('progressContainer').style.display = 'block';

            // 타이머 시작
            monitoringInterval = setInterval(updateMonitoringProgress, 1000);
        } else {
            alert('Failed to start monitoring: ' + result.message);
        }
    } catch (error) {
        console.error('Error starting monitoring:', error);
        alert('Error starting monitoring');
    }
}

// 모니터링 진행 상황 업데이트
function updateMonitoringProgress() {
    const elapsed = Math.floor((Date.now() - monitoringStartTime) / 1000);
    const remaining = Math.max(0, monitoringDuration - elapsed);
    const progress = Math.min(100, (elapsed / monitoringDuration) * 100);

    const minutes = Math.floor(remaining / 60);
    const seconds = remaining % 60;

    document.getElementById('statusText').textContent =
        `Monitoring Active (${minutes}:${seconds.toString().padStart(2, '0')})`;
    document.getElementById('progressBar').style.width = `${progress}%`;
    document.getElementById('progressText').textContent = `${progress.toFixed(0)}%`;

    if (remaining <= 0) {
        finishMonitoring();
    }
}

// 모니터링 완료
function finishMonitoring() {
    clearInterval(monitoringInterval);
    isMonitoring = false;

    document.getElementById('startBtn').disabled = false;
    document.getElementById('stopBtn').disabled = true;
    document.getElementById('downloadBtn').disabled = false;
    document.getElementById('statusText').textContent = 'Monitoring Complete';
    document.getElementById('statusText').classList.remove('monitoring-active');

    alert('5-minute monitoring completed! You can now download the PDF report.');
}

// 모니터링 중지
async function stopMonitoring() {
    try {
        const response = await fetch('/api/stop-monitoring', {
            method: 'POST'
        });
        const result = await response.json();

        if (result.success) {
            clearInterval(monitoringInterval);
            isMonitoring = false;

            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
            document.getElementById('downloadBtn').disabled = false;
            document.getElementById('statusText').textContent = 'Monitoring Stopped';
            document.getElementById('statusText').classList.remove('monitoring-active');
            document.getElementById('progressContainer').style.display = 'none';
        }
    } catch (error) {
        console.error('Error stopping monitoring:', error);
    }
}

// PDF 다운로드
function downloadPDF() {
    window.location.href = '/api/download-pdf';
}
