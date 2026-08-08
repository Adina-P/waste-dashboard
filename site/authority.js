(async function () {
  const data = await loadWasteData();
  const years = data.years;
  const authority = data.authorities.find((a) => a.slug === window.AUTHORITY_SLUG);
  if (!authority) return;

  const rowsHtml = years
    .map((y) => {
      const d = authority.years[String(y)] || {};
      if (!d.reported) {
        return `<tr><td>${y}</td><td colspan="4" class="not-reported">לא דיווחה</td></tr>`;
      }
      return `<tr>
        <td>${y}</td>
        <td>${fmtPct(d.pct_recycled)}</td>
        <td>${fmtPct(d.pct_landfilled)}</td>
        <td>${fmtNum(d.total_waste_tons)}</td>
        <td>${d.kg_per_capita_day ?? "—"}</td>
      </tr>`;
    })
    .reverse()
    .join("");
  document.querySelector("#authority-year-rows").innerHTML = rowsHtml;

  const authorityPct = years.map((y) => authority.years[String(y)]?.pct_recycled ?? null);
  const nationalPct = years.map((y) => data.national[String(y)]?.pct_recycled ?? null);
  const target = years.map(() => data.targets_2030.pct_recycled);

  const root = getComputedStyle(document.documentElement);
  const c = (name) => root.getPropertyValue(name).trim();

  new Chart(document.getElementById("trend-chart"), {
    type: "line",
    data: {
      labels: years,
      datasets: [
        {
          label: authority.name_he,
          data: authorityPct,
          borderColor: c("--series-1"),
          backgroundColor: c("--series-1"),
          borderWidth: 2,
          pointRadius: 3,
          spanGaps: true,
          tension: 0.15,
        },
        {
          label: "ממוצע ארצי",
          data: nationalPct,
          borderColor: c("--text-muted"),
          backgroundColor: c("--text-muted"),
          borderWidth: 2,
          borderDash: [4, 3],
          pointRadius: 0,
          tension: 0.15,
        },
        {
          label: "יעד 2030",
          data: target,
          borderColor: c("--series-3"),
          backgroundColor: c("--series-3"),
          borderWidth: 1.5,
          borderDash: [2, 3],
          pointRadius: 0,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, max: 100, ticks: { callback: (v) => v + "%" }, grid: { color: c("--gridline") } },
        x: { grid: { display: false } },
      },
    },
  });
})();
