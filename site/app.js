// Shared utilities for the waste dashboard static site.

function dataPath() {
  const inSubdir = location.pathname.includes("/authority/") || location.pathname.includes("/en/");
  return inSubdir ? "../data/waste.json" : "data/waste.json";
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

// Generic click-to-sort for any table.ranked with data-key headers and
// data-sort attributes on cells (falls back to cell text if data-sort is absent).
function makeSortableTable(table) {
  if (!table) return;
  const headers = table.querySelectorAll("thead th[data-key]");
  const tbody = table.querySelector("tbody");
  headers.forEach((th, colIndex) => {
    th.addEventListener("click", () => {
      const wasAsc = th.classList.contains("sorted") && th.classList.contains("asc");
      const asc = !wasAsc;
      headers.forEach((h) => h.classList.remove("sorted", "asc"));
      th.classList.add("sorted");
      if (asc) th.classList.add("asc");

      const rows = Array.from(tbody.querySelectorAll("tr"));
      rows.sort((a, b) => {
        const ac = a.children[colIndex];
        const bc = b.children[colIndex];
        const av = ac.dataset.sort ?? ac.textContent.trim();
        const bv = bc.dataset.sort ?? bc.textContent.trim();
        const an = parseFloat(av);
        const bn = parseFloat(bv);
        const cmp = !isNaN(an) && !isNaN(bn) ? an - bn : String(av).localeCompare(String(bv), "he");
        return asc ? cmp : -cmp;
      });
      rows.forEach((r) => tbody.appendChild(r));
    });
  });
}

if (typeof Chart !== "undefined") {
  Chart.defaults.font.family = "system-ui, -apple-system, 'Segoe UI', sans-serif";
  Chart.defaults.color = getComputedStyle(document.documentElement).getPropertyValue("--text-secondary").trim() || "#52514e";
  Chart.defaults.borderColor = getComputedStyle(document.documentElement).getPropertyValue("--gridline").trim() || "#e1e0d9";
}
