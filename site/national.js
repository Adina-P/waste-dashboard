(async function () {
  const lang = window.SITE_LANG || "he";
  const rtl = lang !== "en";
  const t =
    lang === "en"
      ? {
          recycled: "Recycling & recovery",
          landfilled: "Landfilling",
          material: {
            organic: "Organic material",
            yard_waste: "Yard waste",
            paper: "Paper",
            cardboard: "Cardboard",
            plastic: "Plastic",
            glass: "Glass",
            metal: "Metal",
            other: "Other",
          },
          current: (year) => `Current (${year})`,
          target2030: "2030 target",
          localAuthority: "Local authority",
          scatterTooltip: (name, pop, pct) => `${name}: ${pop} residents, ${pct}%`,
          populationLog: "Population (logarithmic scale)",
          pctRecycled: "% recycled",
        }
      : {
          recycled: "מיחזור והשבה",
          landfilled: "הטמנה",
          material: {
            organic: "חומר אורגני",
            yard_waste: "גזם",
            paper: "נייר",
            cardboard: "קרטון",
            plastic: "פלסטיק",
            glass: "זכוכית",
            metal: "מתכת",
            other: "אחר",
          },
          current: (year) => `מצב נוכחי (${year})`,
          target2030: "יעד 2030",
          localAuthority: "רשות מקומית",
          scatterTooltip: (name, pop, pct) => `${name}: ${pop} תושבים, ${pct}%`,
          populationLog: "אוכלוסייה (סקאלה לוגריתמית)",
          pctRecycled: "% מיחזור",
        };

  const data = await loadWasteData();
  const years = data.years;
  const root = getComputedStyle(document.documentElement);
  const c = (name) => root.getPropertyValue(name).trim();
  const authorityName = (a) => (lang === "en" ? a.name_en : a.name_he);

  const recycled = years.map((y) => data.national[String(y)].pct_recycled);
  const landfilled = years.map((y) => data.national[String(y)].pct_landfilled);

  new Chart(document.getElementById("national-chart"), {
    type: "bar",
    data: {
      labels: years,
      datasets: [
        { label: t.recycled, data: recycled, backgroundColor: c("--series-1"), stack: "s" },
        { label: t.landfilled, data: landfilled, backgroundColor: c("--series-6"), stack: "s" },
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
    { key: "organic", label: t.material.organic, color: c("--series-1") },
    { key: "yard_waste", label: t.material.yard_waste, color: c("--series-2") },
    { key: "paper", label: t.material.paper, color: c("--series-3") },
    { key: "cardboard", label: t.material.cardboard, color: c("--series-4") },
    { key: "plastic", label: t.material.plastic, color: c("--series-5") },
    { key: "glass", label: t.material.glass, color: c("--series-6") },
    { key: "metal", label: t.material.metal, color: c("--series-7") },
    { key: "other", label: t.material.other, color: c("--series-8") },
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
      rtl,
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
      labels: [t.landfilled, t.recycled],
      datasets: [
        { label: t.current(latestYear), data: [n.pct_landfilled, n.pct_recycled], backgroundColor: c("--series-6") },
        { label: t.target2030, data: [targets.pct_landfilled, targets.pct_recycled], backgroundColor: c("--series-3") },
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

  const reportingLatest = data.authorities
    .map((a) => ({ name: authorityName(a), pop: a.population, pct: a.years[latestYear]?.pct_recycled }))
    .filter((a) => a.pct !== null && a.pct !== undefined);

  const sorted = [...reportingLatest].sort((a, b) => b.pct - a.pct);
  const leaders = sorted.slice(0, 10);
  const laggards = sorted.slice(-10).reverse();

  function rankBarChart(canvasId, rows, color) {
    new Chart(document.getElementById(canvasId), {
      type: "bar",
      data: {
        labels: rows.map((r) => r.name),
        datasets: [{ data: rows.map((r) => r.pct), backgroundColor: color }],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        rtl,
        plugins: { legend: { display: false } },
        scales: {
          x: { max: 100, ticks: { callback: (v) => v + "%" }, grid: { color: c("--gridline") } },
          y: { grid: { display: false } },
        },
      },
    });
  }
  rankBarChart("leaders-chart", leaders, c("--good"));
  rankBarChart("laggards-chart", laggards, c("--critical"));

  const scatterPoints = data.authorities
    .map((a) => ({ x: a.population, y: a.years[latestYear]?.pct_recycled, name: authorityName(a) }))
    .filter((p) => p.x !== null && p.x !== undefined && p.y !== null && p.y !== undefined);

  new Chart(document.getElementById("scatter-chart"), {
    type: "scatter",
    data: {
      datasets: [
        {
          label: t.localAuthority,
          data: scatterPoints,
          backgroundColor: c("--series-1"),
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      rtl,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => t.scatterTooltip(ctx.raw.name, fmtNum(ctx.raw.x), ctx.raw.y.toFixed(1)),
          },
        },
      },
      scales: {
        x: {
          type: "logarithmic",
          title: { display: true, text: t.populationLog, color: c("--text-secondary") },
          ticks: { callback: (v) => fmtNum(v), color: c("--text-secondary") },
          grid: { color: c("--gridline") },
        },
        y: {
          max: 100,
          title: { display: true, text: t.pctRecycled, color: c("--text-secondary") },
          ticks: { callback: (v) => v + "%" },
          grid: { color: c("--gridline") },
        },
      },
    },
  });
})();
