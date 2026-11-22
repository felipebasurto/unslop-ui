import Chart from "chart.js/auto";
import ChartDataLabels from "chartjs-plugin-datalabels";

export function renderRevenue(canvas, months, thisYear, lastYear) {
  return new Chart(canvas, {
    type: "line",
    plugins: [ChartDataLabels],
    data: {
      labels: months,
      datasets: [
        { label: "This year", data: thisYear, borderColor: "#2563eb" },
        { label: "Last year", data: lastYear, borderColor: "#94a3b8" },
      ],
    },
    options: {
      plugins: {
        title: { display: true, text: "Line chart of monthly revenue" },
        subtitle: { display: true, text: "Each point represents one month. Hover over a point to see the exact value." },
        legend: { display: true, position: "bottom" },
        datalabels: { display: true },
      },
      scales: {
        x: { grid: { color: "#6b7280", lineWidth: 2 }, border: { display: true, width: 2 } },
        y: { grid: { color: "#6b7280", lineWidth: 2 }, border: { display: true, width: 2 } },
      },
    },
  });
}
