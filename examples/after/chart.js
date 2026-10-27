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
        title: { display: true, text: "Weekly active users" },
        legend: { display: false },
        datalabels: {
          display: (ctx) => ctx.dataIndex === ctx.dataset.data.length - 1,
          formatter: (value, ctx) => `${ctx.dataset.label} ${value}`,
          align: "right",
          offset: 8,
        },
      },
      scales: {
        x: { grid: { color: "#e5e7eb", lineWidth: 1 }, border: { display: true, width: 1, color: "#d1d5db" } },
        y: { grid: { color: "#e5e7eb", lineWidth: 1 }, border: { display: false }, ticks: { stepSize: 25 } },
      },
    },
  });
}
