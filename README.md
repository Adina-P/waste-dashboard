# מדד הפסולת — Israel Municipal Waste Dashboard

A free, public, Hebrew-first dashboard showing every Israeli local authority's real waste and recycling numbers, tracked against the national 2030 targets (20% landfilling / 54% recycling).

**Live site:** https://adina-p.github.io/waste-dashboard/

## What's here

- Ranked, sortable, searchable table of all ~257 local authorities: % recycled, kg/capita/day, tons, year-over-year trend
- Per-authority trend pages vs. national average and the 2030 target
- National overview: recycling vs. landfilling over time, material composition (paper/plastic/organic/etc.), gap to target
- "Wall of silence": authorities that don't report data
- [Methodology](https://adina-p.github.io/waste-dashboard/methodology.html): every source, every calculation, every known data limitation, stated plainly

## Data sources

Central Bureau of Statistics (CBS), data.gov.il, and the Knesset Research Center. Full citations on the [methodology page](https://adina-p.github.io/waste-dashboard/methodology.html) and in [`data/SOURCES.md`](data/SOURCES.md).

## Repo structure

```
data/raw/        # downloaded source files, as-is
data/processed/  # waste.csv — the cleaned, tidy output of the pipeline
data/SOURCES.md  # manifest of every data source and where it came from
data/CONFLICTS.md # data discrepancies found and how they were resolved
pipeline/        # Python scripts: raw files -> waste.csv -> site/
site/            # the static site itself (plain HTML/CSS/JS + Chart.js)
```

## Running the pipeline

```bash
uv run --with pandas --with xlrd python3 pipeline/build.py            # data/raw -> data/processed/waste.csv
uv run --with pandas --with xlrd python3 pipeline/build_site_data.py  # -> site/data/waste.json
uv run --with pandas --with xlrd python3 pipeline/generate_site.py    # -> site/*.html
```

No database, no build chain, no framework — the whole site is static files, deployed via GitHub Pages.

## Status

v1, actively maintained. Data is not yet auto-updating; re-run the pipeline when CBS publishes new figures. Known gaps (district, socioeconomic cluster, a few unmatched authorities) are documented in the methodology page rather than hidden.
