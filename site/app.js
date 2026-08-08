// Shared utilities for the waste dashboard static site.

function dataPath() {
  return location.pathname.includes("/authority/") ? "../data/waste.json" : "data/waste.json";
}

async function loadWasteData() {
  const res = await fetch(dataPath());
  return res.json();
}

function fmtPct(v) {
  return v === null || v === undefined ? "—" : v.toFixed(1) + "%";
}

function fmtNum(v) {
  return v === null || v === undefined ? "—" : Math.round(v).toLocaleString("he-IL");
}

function latestReportedYear(authority, years) {
  for (let i = years.length - 1; i >= 0; i--) {
    const y = String(years[i]);
    if (authority.years[y] && authority.years[y].reported) return y;
  }
  return null;
}

Chart.defaults.font.family = "system-ui, -apple-system, 'Segoe UI', sans-serif";
Chart.defaults.color = getComputedStyle(document.documentElement).getPropertyValue("--text-secondary").trim() || "#52514e";
Chart.defaults.borderColor = getComputedStyle(document.documentElement).getPropertyValue("--gridline").trim() || "#e1e0d9";
