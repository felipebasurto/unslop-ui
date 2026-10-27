import Chart from "chart.js/auto";

export function renderWau(canvas, weeks, values) {
  return new Chart(canvas, {
    type: "line",
    data: { labels: weeks, datasets: [{ label: "Weekly active users", data: values }] },
    options: {
      plugins: {
        title: { display: true, text: "📈 Line chart of weekly active users" },
        subtitle: { display: true, text: "Each point represents one week — hover over a point to see the exact value." },
        legend: { display: true },
        datalabels: { display: true },
      },
    },
  });
}
