(async function () {
  const data = await loadWasteData();
  const years = data.years;
  const root = getComputedStyle(document.documentElement);
  const c = (name) => root.getPropertyValue(name).trim();

  const recycled = years.map((y) => data.national[String(y)].pct_recycled);
  const landfilled = years.map((y) => data.national[String(y)].pct_landfilled);

  new Chart(document.getElementById("national-chart"), {
    type: "bar",
    data: {
      labels: years,
      datasets: [
        { label: "מיחזור והשבה", data: recycled, backgroundColor: c("--series-1"), stack: "s" },
        { label: "הטמנה", data: landfilled, backgroundColor: c("--series-6"), stack: "s" },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { stacked: true, grid: { display: false } },
        y: { stacked: true, max: 100, ticks: { callback: (v) => v + "%" }, grid: { color: c("--gridline") } },
      },
    },
  });

  const materialSeries = [
    { key: "organic", label: "חומר אורגני", color: c("--series-1") },
    { key: "yard_waste", label: "גזם", color: c("--series-2") },
    { key: "paper", label: "נייר", color: c("--series-3") },
    { key: "cardboard", label: "קרטון", color: c("--series-4") },
    { key: "plastic", label: "פלסטיק", color: c("--series-5") },
    { key: "glass", label: "זכוכית", color: c("--series-6") },
    { key: "metal", label: "מתכת", color: c("--series-7") },
    { key: "other", label: "אחר", color: c("--series-8") },
  ];

  new Chart(document.getElementById("materials-chart"), {
    type: "bar",
    data: {
      labels: years,
      datasets: materialSeries.map((s) => ({
        label: s.label,
        data: years.map((y) => data.national_materials[String(y)][s.key]),
        backgroundColor: s.color,
        stack: "m",
      })),
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      rtl: true,
      plugins: { legend: { position: "bottom", labels: { usePointStyle: true, boxWidth: 8 } } },
      scales: {
        x: { stacked: true, grid: { display: false } },
        y: { stacked: true, ticks: { callback: (v) => fmtNum(v) }, grid: { color: c("--gridline") } },
      },
    },
  });

  const latestYear = String(years[years.length - 1]);
  const n = data.national[latestYear];
  const targets = data.targets_2030;

  new Chart(document.getElementById("gap-chart"), {
    type: "bar",
    data: {
      labels: ["הטמנה", "מיחזור"],
      datasets: [
        { label: `מצב נוכחי (${latestYear})`, data: [n.pct_landfilled, n.pct_recycled], backgroundColor: c("--series-6") },
        { label: "יעד 2030", data: [targets.pct_landfilled, targets.pct_recycled], backgroundColor: c("--series-3") },
      ],
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: "bottom" } },
      scales: {
        x: { max: 100, ticks: { callback: (v) => v + "%" }, grid: { color: c("--gridline") } },
        y: { grid: { display: false } },
      },
    },
  });
})();
