# Data Source Audit (Phase 1) — Israel Municipal Waste Dashboard

Audited: 2026-07-19. Status of each source: located ✅ / needs browser session ⚠️ / to download in Claude Code project ⬇️

## 1. CBS — per-authority waste tonnage & recycling (PRIMARY SOURCE)

**"פסולת שנאספה ברשויות המקומיות 2014–2023"** — dedicated multi-year dataset. ⚠️
- Page: https://www.cbs.gov.il/he/publications/Pages/2019/פסולת-שנאספה-ברשויות-המקומיות-2014-2017.aspx (page title now shows 2014–2023 — CBS updates the same page)
- CBS pages are JavaScript-rendered; the Excel download links must be grabbed in a browser session (first task in the Claude Code project).
- Expected content: tons collected, treatment breakdown, per authority per year. This alone may cover the whole v1 year range.

**"הרשויות המקומיות בישראל" annual publication** (backup/context source) ✅
- 2023 edition (pub. #1987, published 2026): https://www.cbs.gov.il/he/publications/Pages/2026/הרשויות-המקומיות-בישראל-2023.aspx
- 2022: files under https://www.cbs.gov.il/he/publications/doclib/2024/local_authorities22_1957/
- 2018: https://www.cbs.gov.il/he/publications/DocLib/2020/local_authorities18_1797/
- 2017: .../2019/local_authorities17_1759/ · 2015: .../2017/local_authorities15_1683/
- DocLib URL pattern is stable: `/he/publications/DocLib/{pub_year}/local_authorities{data_year}_{pub_number}/`. Excel appendix files sit alongside the PDFs — enumerate in browser once, then direct-download.
- Also contains population + socioeconomic cluster per authority (needed for normalization).

**CBS waste survey PDFs** (methodology + national totals) ✅
- סקר פסולת ומחזור 2021/2022: https://www.cbs.gov.il/he/publications/DocLib/2019/לוחות%20תלושים/סקר%20פסולת%20ומחזור%20ברשויות%202021.pdf

**⚠️ Key caveat discovered: CBS data lags ~2–3 years** (2023 data published in 2026). Direct implication for the reform question — see §5.

## 2. data.gov.il — MoEP waste information system ✅ (direct URLs, updated daily)

Dataset "מערכת מידע פסולת — נספחים" (id `e444962a-0f58-429c-bc3c-f63786be1cfe`), 12 resources, all direct-download:
- רשויות מקומיות (canonical authority list + reporting codes): https://data.gov.il/dataset/e444962a-0f58-429c-bc3c-f63786be1cfe/resource/4e041600-1ce3-4780-9e3f-3d2ce1561dea/download/4e041600-1ce3-4780-9e3f-3d2ce1561dea.csv
- סוגי פסולת (waste type codes): .../resource/ca71e149-49f1-48a2-b319-b27be21e3e21/download/ca71e149-49f1-48a2-b319-b27be21e3e21.csv
- Facility lists (XLSX): landfills (mixed + construction), recycling plants (mixed + construction), transfer stations (mixed, construction, pruning/גזם), waste-to-energy plants, organic waste treatment sites (added Nov 2025 — reform-relevant!)
  - Organic treatment sites: .../resource/fe5fe429-895c-4bfe-8941-eb01aff35547/download/fe5fe429-895c-4bfe-8941-eb01aff35547.xlsx
  - Full list: query CKAN API `package_show?id=e444962a-0f58-429c-bc3c-f63786be1cfe`
- Note: these are **infrastructure lists, not tonnage**. Use for: canonical authority codes, facility-capacity map, reform progress tracking.

**מפל"ס (PRTR)** — facility-level emissions & waste transfers, annual, CC-BY ✅
- https://data.gov.il/dataset/5fc5c912-4fa5-4474-93c1-326e505e22cf/resource/7ad8ddc7-87f4-45f9-84e4-d7f972662153/download/7ad8ddc7-87f4-45f9-84e4-d7f972662153.csv (~6 MB)

CKAN search found 16 waste datasets total — re-run `package_search?q=פסולת` in the project for the full inventory.

## 3. Knesset Research & Information Center ✅

- **Jan 2026 waste report** (most current national numbers, 2024 data): https://fs.knesset.gov.il/25/Committees/25_cs_mmm_11061789.pdf
- 2022 waste treatment report: https://fs.knesset.gov.il/globaldocs/MMM/b91b5ecf-5569-ec11-8142-00155d0401c3/2_b91b5ecf-5569-ec11-8142-00155d0401c3_11_19596.pdf

## 4. MoEP pages ⚠️ (JS-rendered, read in browser)

- Waste facts: https://www.gov.il/he/pages/waste_facts_and_figures
- Waste & recycling topic hub: https://www.gov.il/he/departments/topics/waste_and_recycling

## 5. Reform tracking sources (for the "reform vs. reality" panel)

The current reform (2025 Arrangements Law + MoEP strategy): three-bin source separation (brown=organic, orange=dry recyclables, green=residual), economic incentives, and transfer of waste management from MoEP to a new independent National Waste Authority. Targets: 20% landfill / 54% recycling by 2030; 10–15% waste reduction at source; 35–50% source-separation rates.

- infospot.co.il — sector news portal, best ongoing tracker: https://infospot.co.il/scp/פסולת_עירונית_ביתית and https://infospot.co.il/n/landfill_development
- Zalul position paper (Feb 2025): https://zalul.org.il/emdapsolet/
- Neaman Institute on organic separation: https://www.neaman.org.il/en/separation-of-organic-waste/
- Ynet critique of returning to the failed 2009 program: https://www.ynet.co.il/environment-science/article/H1TT00daJu
- Key facility fact for context: ~70% of organic waste reaching sorting facilities still goes to landfill because green-bin organics are contaminated — clean compost requires source separation (infospot).

## Download status

⬇️ Actual file downloads + parsing happen in the Claude Code project (full network + browser there). First session there: (1) open the two ⚠️ CBS pages, harvest Excel URLs; (2) `package_show` on data.gov.il and pull all 12+ resources; (3) download the two Knesset PDFs; (4) commit everything to `data/raw/` with this file as the manifest.

**Note:** the sandboxed browser in this environment cannot reach cbs.gov.il at all (network-level block, confirmed 2026-07-19 — even the bare domain root was denied while other sites loaded fine). CBS downloads must be done manually by the user in their own browser.

### Downloaded — CBS multi-year waste dataset (2026-07-19)

Source page: https://www.cbs.gov.il/he/publications/Pages/2019/פסולת-שנאספה-ברשויות-המקומיות-2014-2017.aspx (title now reads 2014–2024)

Saved to `data/raw/cbs_waste_2014_2024/`:
- `table1_separation_method_by_district_2014-2024.xls` — לוח 1: פסולת ביתית ומסחרית שנאספה והועברה למחזור והשבה לפי אופן הפרדה, מחוז ונפה, 2014–2024
- `table2_recycled_materials_by_district_2014-2024.xls` — לוח 2: ...לפי חומרים ממוחזרים נבחרים, מחוז ונפה, 2014–2024
- `table3_by_municipal_status_and_treatment_2014-2024.xls` — לוח 3: פסולת ביתית ומסחרית שנאספה, לפי מעמד מוניציפלי ואופן טיפול, 2014–2024
- `table4_by_treatment_and_authority_2014-2024.xls` — לוח 4: פסולת ביתית ומסחרית שנאספה, לפי אופן טיפול ורשות מקומית, 2014–2024 — **this is the per-authority tonnage table, primary input for the core schema**

Not yet parsed/validated — contents (sheet structure, header rows, authority coverage) still need to be inspected in Phase 2.

Still outstanding: the annual "הרשויות המקומיות בישראל" 2023 edition Excel appendix (population/socioeconomic data) — https://www.cbs.gov.il/he/publications/Pages/2026/הרשויות-המקומיות-בישראל-2023.aspx

### Downloaded — data.gov.il waste information system (2026-07-19)

Dataset `e444962a-0f58-429c-bc3c-f63786be1cfe`, all 12 resources, saved to `data/raw/data_gov_il_waste_info/`:
- `local_authorities.csv` — canonical authority names + CBS authority IDs — **the join key for every other source**. 259 rows. Was Windows-1255 encoded; converted to UTF-8.
- `waste_types.csv` — waste material type codes. Was Windows-1255; converted to UTF-8.
- `energy_recovery_facilities.csv` — 1 facility row. Was Windows-1255; converted to UTF-8.
- `landfills_construction_waste.xlsx`, `landfills_mixed_waste.xlsx`
- `recycling_construction_waste.xlsx`, `recycling_mixed_waste.xlsx`
- `transfer_stations_construction_waste.xlsx`, `transfer_stations_mixed_waste.xlsx`, `transfer_stations_vegetation_waste.xlsx`
- `organic_waste_treatment_sites.xlsx`
- `mixed_waste_sites_contact_info.xlsx`

Note: **CSV files from data.gov.il/CBS come Windows-1255 encoded, not UTF-8** — always check/convert (`iconv -f WINDOWS-1255 -t UTF-8`) before parsing. XLSX files are unaffected (Excel format stores encoding internally). The PRTR CSV below was the exception — already UTF-8 with a BOM.

### Downloaded — PRTR facility-level data (2026-07-19)

`data/raw/prtr/prtr_facilities.csv` — dataset `5fc5c912-4fa5-4474-93c1-326e505e22cf`. Already UTF-8 (BOM), no conversion needed.

### Downloaded — Knesset reports (2026-07-19)

`data/raw/knesset/knesset_waste_report_2026-01.pdf` and `data/raw/knesset/knesset_waste_treatment_report_2022.pdf`.

None of these files have been parsed/validated yet — that's Phase 2.

### Downloaded — population & socioeconomic cluster (2026-07-19)

The 2023 "הרשויות המקומיות בישראל" publication's own download tabs turned out not to have this (only per-indicator "map data" exports — tax, teacher ratio, unemployment, car age — and PDF-only municipal profiles). Found equivalent data as standalone data.gov.il datasets instead:

`data/raw/cbs_population_socioeconomic/`:
- `population_by_locality_2022.csv` — CBS 2022 Census, dataset `3bd97fde-6cc3-456d-ab63-1caad16b2b6a` (resource: אוכלוסייה ומשקי בית לפי יישוב). Columns: LocalityCode, LocNameHeb, Total_Population, Residents_in_collective_residences_and_institutions, Foreigners, Households, Average_size_of_household. 1223 rows. Was Windows-1255; converted to UTF-8.
- `socioeconomic_cluster_2019.csv` — dataset `df3b0e8d-b76a-4186-a6e1-df8eada5ef27` (אשכול כלכלי חברתי של יישובים ומועצות 2019). Columns include LOCALITY SYMBOL, HEBREW/NAME OF LOCALITY, **ESHKOL 2019** (the cluster value, 1-10 scale), plus regional council name where applicable. Already UTF-8 (BOM). Has ~200 trailing empty columns per row (Excel export artifact) — trim on parse. **2019 is the latest available** — CBS updates socioeconomic clusters infrequently (previous editions 2013, 2015, 2017).

Note: no explicit "district" (מחוז) column spotted yet in either file — check during Phase 2 parsing whether it can be derived (e.g. from the CBS waste tables' own district/נפה columns) before treating it as missing.
