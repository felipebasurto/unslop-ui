import Chart from "chart.js/auto";
import ChartDataLabels from "chartjs-plugin-datalabels";

export function renderWau(canvas, weeks, thisYear, lastYear) {
  return new Chart(canvas, {
    type: "line",
    plugins: [ChartDataLabels],
    data: {
      labels: weeks,
      datasets: [
        { label: "This year", data: thisYear, borderWidth: 3, pointRadius: 5 },
        { label: "Last year", data: lastYear, borderWidth: 3, pointRadius: 5 },
      ],
    },
    options: {
      plugins: {
        title: { display: true, text: "📈 Line chart of weekly active users" },
        subtitle: { display: true, text: "Each point represents one week — hover over a point to see the exact value." },
        legend: { display: true, position: "bottom" },
        datalabels: { display: true },
      },
      scales: {
        x: { grid: { color: "#9ca3af", lineWidth: 2 }, border: { display: true, width: 2, color: "#111827" } },
        y: { grid: { color: "#9ca3af", lineWidth: 2 }, border: { display: true, width: 2, color: "#111827" }, ticks: { stepSize: 25 } },
      },
    },
  });
}
