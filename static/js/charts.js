/**
 * FitPulse Dynamic Chart.js Analytics Dashboard
 */

let weightChartInstance = null;
let workoutChartInstance = null;
let typeChartInstance = null;
let goalChartInstance = null;

// Global Chart.js styling defaults for dark theme
if (window.Chart) {
    Chart.defaults.color = '#94a3b8';
    Chart.defaults.font.family = "'Plus Jakarta Sans', sans-serif";
    Chart.defaults.plugins.tooltip.backgroundColor = '#1e293b';
    Chart.defaults.plugins.tooltip.borderColor = 'rgba(255, 255, 255, 0.1)';
    Chart.defaults.plugins.tooltip.borderWidth = 1;
    Chart.defaults.plugins.tooltip.padding = 10;
    Chart.defaults.plugins.tooltip.cornerRadius = 8;
    Chart.defaults.plugins.legend.labels.usePointStyle = true;
}

function loadProgressData(days = '30') {
    const loadingIndicators = document.querySelectorAll('.chart-spinner');
    loadingIndicators.forEach(el => el.classList.remove('d-none'));

    fetch(`/api/progress-data?days=${days}`)
        .then(res => res.json())
        .then(data => {
            loadingIndicators.forEach(el => el.classList.add('d-none'));
            renderWeightChart(data.weight);
            renderWorkoutChart(data.workouts);
            renderTypeChart(data.types);
            renderGoalChart(data.goals);
        })
        .catch(err => {
            console.error('Error loading analytics data:', err);
            loadingIndicators.forEach(el => el.classList.add('d-none'));
        });
}

function renderWeightChart(weightData) {
    const canvas = document.getElementById('weightProgressChart');
    const emptyNotice = document.getElementById('weightEmptyNotice');
    if (!canvas) return;

    if (!weightData || !weightData.has_data) {
        canvas.classList.add('d-none');
        if (emptyNotice) emptyNotice.classList.remove('d-none');
        return;
    }

    canvas.classList.remove('d-none');
    if (emptyNotice) emptyNotice.classList.add('d-none');

    const ctx = canvas.getContext('2d');
    if (weightChartInstance) weightChartInstance.destroy();

    const gradient = ctx.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, 'rgba(16, 185, 129, 0.35)');
    gradient.addColorStop(1, 'rgba(16, 185, 129, 0.0)');

    weightChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: weightData.labels,
            datasets: [{
                label: 'Weight (kg)',
                data: weightData.data,
                borderColor: '#10b981',
                backgroundColor: gradient,
                fill: true,
                tension: 0.35,
                borderWidth: 3,
                pointBackgroundColor: '#10b981',
                pointBorderColor: '#0f172a',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 7
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8' }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: {
                        color: '#94a3b8',
                        callback: val => `${val} kg`
                    }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

function renderWorkoutChart(workoutData) {
    const canvas = document.getElementById('workoutProgressChart');
    const emptyNotice = document.getElementById('workoutEmptyNotice');
    if (!canvas) return;

    if (!workoutData || !workoutData.has_data) {
        canvas.classList.add('d-none');
        if (emptyNotice) emptyNotice.classList.remove('d-none');
        return;
    }

    canvas.classList.remove('d-none');
    if (emptyNotice) emptyNotice.classList.add('d-none');

    const ctx = canvas.getContext('2d');
    if (workoutChartInstance) workoutChartInstance.destroy();

    workoutChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: workoutData.labels,
            datasets: [
                {
                    type: 'bar',
                    label: 'Duration (mins)',
                    data: workoutData.durations,
                    backgroundColor: 'rgba(6, 182, 212, 0.7)',
                    borderColor: '#06b6d4',
                    borderWidth: 1,
                    borderRadius: 6,
                    yAxisID: 'y'
                },
                {
                    type: 'line',
                    label: 'Calories Burned (kcal)',
                    data: workoutData.calories,
                    borderColor: '#f59e0b',
                    backgroundColor: 'transparent',
                    borderWidth: 2.5,
                    pointBackgroundColor: '#f59e0b',
                    pointRadius: 4,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' }
                },
                y: {
                    type: 'linear',
                    position: 'left',
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    title: { display: true, text: 'Minutes', color: '#94a3b8' }
                },
                y1: {
                    type: 'linear',
                    position: 'right',
                    grid: { drawOnChartArea: false },
                    title: { display: true, text: 'Calories (kcal)', color: '#f59e0b' }
                }
            }
        }
    });
}

function renderTypeChart(typeData) {
    const canvas = document.getElementById('workoutTypeChart');
    const emptyNotice = document.getElementById('typeEmptyNotice');
    if (!canvas) return;

    if (!typeData || !typeData.has_data) {
        canvas.classList.add('d-none');
        if (emptyNotice) emptyNotice.classList.remove('d-none');
        return;
    }

    canvas.classList.remove('d-none');
    if (emptyNotice) emptyNotice.classList.add('d-none');

    const ctx = canvas.getContext('2d');
    if (typeChartInstance) typeChartInstance.destroy();

    const colors = ['#10b981', '#06b6d4', '#6366f1', '#a855f7', '#f59e0b', '#f43f5e', '#ec4899', '#14b8a6'];

    typeChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: typeData.labels,
            datasets: [{
                data: typeData.counts,
                backgroundColor: colors.slice(0, typeData.labels.length),
                borderColor: '#1e293b',
                borderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { boxWidth: 12, padding: 15 }
                }
            },
            cutout: '65%'
        }
    });
}

function renderGoalChart(goalData) {
    const canvas = document.getElementById('goalStatusChart');
    const emptyNotice = document.getElementById('goalEmptyNotice');
    if (!canvas) return;

    if (!goalData || !goalData.has_data) {
        canvas.classList.add('d-none');
        if (emptyNotice) emptyNotice.classList.remove('d-none');
        return;
    }

    canvas.classList.remove('d-none');
    if (emptyNotice) emptyNotice.classList.add('d-none');

    const ctx = canvas.getContext('2d');
    if (goalChartInstance) goalChartInstance.destroy();

    goalChartInstance = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: goalData.labels,
            datasets: [{
                data: goalData.data,
                backgroundColor: ['#3b82f6', '#10b981', '#ef4444'],
                borderColor: '#1e293b',
                borderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { boxWidth: 12, padding: 15 }
                }
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    // Only load if progress page container exists
    if (document.getElementById('progressDashboardContainer')) {
        loadProgressData('30');

        // Range filter pill buttons
        const filterPills = document.querySelectorAll('.progress-range-btn');
        filterPills.forEach(btn => {
            btn.addEventListener('click', (e) => {
                filterPills.forEach(b => b.classList.remove('active', 'btn-emerald'));
                filterPills.forEach(b => b.classList.add('btn-outline-custom'));
                
                btn.classList.add('active', 'btn-emerald');
                btn.classList.remove('btn-outline-custom');

                const days = btn.getAttribute('data-days');
                loadProgressData(days);
            });
        });
    }
});
