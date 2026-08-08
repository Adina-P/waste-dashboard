(async function () {
  const lang = window.SITE_LANG || "he";
  const t =
    lang === "en"
      ? { authorities: (n) => `${n} authorities`, notReported: "Not reported", locale: "en-US" }
      : { authorities: (n) => `${n} רשויות`, notReported: "לא דיווחה", locale: "he" };

  const data = await loadWasteData();
  const years = data.years;
  const latestYear = String(years[years.length - 1]);

  const rows = data.authorities.map((a) => {
    const ly = latestReportedYear(a, years);
    const y = ly ? a.years[ly] : {};
    return {
      slug: a.slug,
      name: lang === "en" ? a.name_en : a.name_he,
      population: a.population,
      population_bucket: a.population_bucket,
      total_waste_tons: y.total_waste_tons ?? null,
      pct_recycled: y.pct_recycled ?? null,
      kg_per_capita_day: y.kg_per_capita_day ?? null,
      trend: y.trend_vs_prev_year ?? null,
      data_year: ly,
      reported_latest: ly === latestYear,
    };
  });

  const tbody = document.querySelector("#ranked-table tbody");
  const searchInput = document.querySelector("#search");
  const popFilter = document.querySelector("#pop-filter");
  const resultCount = document.querySelector("#result-count");
  const headers = document.querySelectorAll("#ranked-table th[data-key]");

  let sortKey = "pct_recycled";
  let sortDir = "desc";

  function trendCell(tr) {
    if (tr === null) return "—";
    const cls = tr > 0 ? "trend-up" : tr < 0 ? "trend-down" : "";
    const arrow = tr > 0 ? "▲" : tr < 0 ? "▼" : "—";
    return `<span class="${cls}">${arrow} ${Math.abs(tr).toFixed(1)}%</span>`;
  }

  const authorityHref = (slug) => (lang === "en" ? `../authority/${slug}.html` : `authority/${slug}.html`);

  function render() {
    const q = searchInput.value.trim();
    const pop = popFilter.value;

    let filtered = rows.filter((r) => {
      if (q && !r.name.includes(q)) return false;
      if (pop && r.population_bucket !== pop) return false;
      return true;
    });

    filtered.sort((a, b) => {
      let av = a[sortKey];
      let bv = b[sortKey];
      if (av === null || av === undefined) av = sortDir === "desc" ? -Infinity : Infinity;
      if (bv === null || bv === undefined) bv = sortDir === "desc" ? -Infinity : Infinity;
      if (typeof av === "string") return sortDir === "asc" ? av.localeCompare(bv, t.locale) : bv.localeCompare(av, t.locale);
      return sortDir === "asc" ? av - bv : bv - av;
    });

    resultCount.textContent = t.authorities(filtered.length);

    tbody.innerHTML = filtered
      .map((r) => {
        const yearCell = r.data_year
          ? r.reported_latest
            ? r.data_year
            : `<span class="not-reported">${r.data_year}*</span>`
          : `<span class="not-reported">${t.notReported}</span>`;
        return `<tr>
          <td class="name"><a href="${authorityHref(r.slug)}">${r.name}</a></td>
          <td>${fmtNum(r.population)}</td>
          <td>${fmtNum(r.total_waste_tons)}</td>
          <td>${fmtPct(r.pct_recycled)}</td>
          <td>${r.kg_per_capita_day !== null ? r.kg_per_capita_day.toFixed(2) : "—"}</td>
          <td>${trendCell(r.trend)}</td>
          <td>${yearCell}</td>
        </tr>`;
      })
      .join("");
  }

  headers.forEach((th) => {
    th.addEventListener("click", () => {
      const key = th.dataset.key;
      if (sortKey === key) {
        sortDir = sortDir === "asc" ? "desc" : "asc";
      } else {
        sortKey = key;
        sortDir = key === "name" ? "asc" : "desc";
      }
      headers.forEach((h) => h.classList.remove("sorted", "asc"));
      th.classList.add("sorted");
      if (sortDir === "asc") th.classList.add("asc");
      render();
    });
  });

  searchInput.addEventListener("input", render);
  popFilter.addEventListener("change", render);

  render();
})();
