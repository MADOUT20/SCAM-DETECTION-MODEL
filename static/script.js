google.charts.load('current', { packages: ['corechart'] });
function switchView(viewId) {
    const windows = document.querySelectorAll('.window');
    windows.forEach(win => win.classList.remove('active'));
    document.getElementById(viewId).classList.add('active');
}

function toggleFaq(btn) {
    const item = btn.parentElement;
    item.classList.toggle('active');
}

const redFlagSeverity = {
    "Upfront fee requested": 4,
    "Unusual payment method requested": 3,
    "Urgent payment pressure": 2,
    "Generic sender identity": 1,
    "Missing company details": 1
};

document.getElementById('analyzeBtn').addEventListener('click', async function () {
    const btn = this;
    const res = document.getElementById('resultBox');
    const text = document.getElementById('emailContent').value;

    if (!text.trim()) {
        res.classList.remove('hidden');
        res.innerHTML = "Please paste an email first.";
        return;
    }

    btn.innerText = "Analyzing...";

    try {
        const response = await fetch("/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text })
        });

        const data = await response.json();
        // ---- PIE CHART: Overall Risk ----
        google.charts.setOnLoadCallback(() => {
            const riskPercent = Math.round(data.final_score);

            const pieData = google.visualization.arrayToDataTable([
                ['Type', 'Value'],
                ['Risk', riskPercent],
                ['Safe', 100 - riskPercent]
            ]);

            const pieOptions = {
                title: 'Overall Risk Percentage',
                backgroundColor: 'transparent',
                pieHole: 0.5,
                pieSliceBorderColor: 'transparent',
                legend: {
                    textStyle: { color: '#aaa' }
                },
                titleTextStyle: {
                    color: '#aaa',
                    fontSize: 14
                },
                slices: {
                    0: { color: '#ff5252' },   // risk
                    1: { color: '#4caf50' }    // safe
                },
                chartArea: {
                    width: '90%',
                    height: '80%'
                }
            };

            const pieChart = new google.visualization.PieChart(
                document.getElementById('risk_pie')
            );
            pieChart.draw(pieData, pieOptions);
        });

        // ---- BAR CHART: Suspicious Indicators ----
        google.charts.setOnLoadCallback(() => {
            const flags = data.red_flags;

            const barArray = [['Indicator', 'Count']];
            flags.forEach(f => {
                const weight = redFlagSeverity[f] || 1;
                barArray.push([f, weight]);
            });

            if (barArray.length === 1) {
                barArray.push(['No suspicious indicators', 0]);
            }

            const barData = google.visualization.arrayToDataTable(barArray);

            const barOptions = {
                title: 'Detected Suspicious Indicators',
                backgroundColor: 'transparent',
                legend: 'none',
                titleTextStyle: { color: '#aaa' },
                hAxis: {
                    textStyle: { color: '#aaa' }
                },
                vAxis: {
                    minValue: 0,
                    maxValue: 5,
                    ticks: [0, 1, 2, 3, 4, 5],
                    textStyle: { color: '#aaa' }
                },
                colors: ['#ff9800'],
                chartArea: {
                    width: '70%',
                    height: '70%'
                }
            };
            
            const barChart = new google.visualization.ColumnChart(
                document.getElementById('flags_bar')
            );
            barChart.draw(barData, barOptions);
        });
        res.classList.remove('hidden');
        res.innerHTML =
            "<strong>Risk:</strong> " + data.final_label + "<br>" +
            "<strong>Red Flags:</strong> " +
            (data.red_flags.length ? data.red_flags.join(", ") : "None") +
            "<br><br><strong>Explanation:</strong><br>" +
            data.explanation;

    } catch (err) {
        res.classList.remove('hidden');
        res.innerHTML = "Error analyzing email.";
    }

    btn.innerText = "Analyze Threat";
});