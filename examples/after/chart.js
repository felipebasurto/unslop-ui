import Chart from "chart.js/auto";

export function renderWau(canvas, weeks, values) {
  return new Chart(canvas, {
    type: "line",
    data: { labels: weeks, datasets: [{ label: "Weekly active users", data: values }] },
    options: {
      plugins: {
        title: { display: true, text: "Weekly active users" },
        legend: { display: false },
      },
    },
  });
}
