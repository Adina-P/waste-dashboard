# Data Conflicts & Known Gaps (Phase 2)

Logged per PROJECT.md's rule: "When a source conflicts with another, log it here and surface the chosen rule in the methodology page."

## Validated against published figures (2026-07-19)

`table4_by_treatment_and_authority_2014-2024.xls`, parsed via `pipeline/parse_cbs_waste.py`, matches PROJECT.md's cited 2024 recycling rates almost exactly:

| Authority | Our value | PROJECT.md cited |
|---|---|---|
| Bat Yam | 39.84% | 39.8% |
| Holon | 38.72% | 38.7% |
| Ramat Gan | 37.85% | 37.8% |
| Jerusalem | 37.44% | 37.4% |
| Tel Aviv-Yafo | 36.48% | 36.5% |

National 2024 landfill rate (summed across reporting authorities): 75.2%, vs. PROJECT.md's cited ~76% (Knesset Research Center). Close match — small gap plausibly explained by differing report vintages/definitions.

## Reporting-rate discrepancy — RESOLVED (2026-07-23)

PROJECT.md stated "only ~120–125 of ~255 local authorities even report waste data." Our parse of `table4` shows a much higher reporting rate: 226–253 authorities/year with actual (non-".." ) data out of 255-257 total rows, across 2014-2024 (2024: 239/257 reporting).

**Root cause found: the "~120" figure is from a different report about a different reporting system, and it is 18 years stale.** Traced via web search to a Knesset Research Center report, **"פסולת ביתית בישראל" (Household Waste in Israel), dated June 2008**: "כ-120 רשויות מקומיות בלבד מדווחות למשרד להגנת הסביבה על כמות הפסולת הנוצרת בתחומן ועל אופן הטיפול בה" — "only ~120 local authorities report to the Ministry of Environmental Protection on the quantity of waste generated in their area and how it's treated." That report also notes MoEP had no sanction power to enforce compliance, and describes a mandatory regulatory reporting requirement under the Cleanliness Maintenance regulations — a completely different mechanism from the CBS statistical survey ("סקר פסולת ומחזור ברשויות המקומיות") that `table4` comes from, and describing conditions as of 2008, not the present.

**Resolution for the site**: the two figures are not in conflict once correctly attributed — they describe different reporting systems, 16+ years apart. PROJECT.md's Mission section has been corrected to remove the stale 2008 figure. The methodology page states our actual, current, sourced coverage rate (226-253 of 255-257 authorities per year in the CBS survey) rather than repeating an unrelated 2008 statistic.

## Total tons undercounts national totals — confirmed, not just plausible

Summed `total_waste_tons` across all reporting authorities for 2024 = 5,897,586.62 tons. CBS's own published TOTAL row in the same `table4` sheet says **6,382,969.63 tons** — which matches PROJECT.md's Knesset-cited ~6.4M almost exactly. Verified directly: summing the raw sheet's total-tons column across all 257 authority rows (both reporting and non-reporting/".." rows) reproduces our 5.90M figure exactly, confirming CBS's own total includes ~485K tons (~7.6%) not attributable to any of the 257 named-authority rows visible in the table — presumably an estimate/allocation for non-reporting authorities that CBS itself computes but doesn't break out per-authority.

**Methodology page must state explicitly**: any summed/aggregate total computed from `data/processed/waste.csv` (e.g. "total waste this year") will run ~7-8% below Israel's official national total, because it only reflects authorities with individually-reported figures. Do not present our summed total as the national total — cite CBS's official aggregate (from the source table's own TOTAL row) for national-level figures instead, and reserve the per-authority table for authority-level figures.

## Authority identifier gaps

- `table4` (the core CBS waste table) has **no CBS authority code column at all** — only English and Hebrew names. `authority_id` in `data/processed/waste.csv` is backfilled via name-match against the 2022 census population file (which does carry locality codes), achieving 80.7% coverage. The ~54 regional councils have no single locality code (only their member villages do), so they get a null `authority_id`.
- Two authorities have no population match in any source we found: **שדות דן** and **שער שומרון** (both regional councils). Neither appears under any name variant in the 2019 socioeconomic-cluster crosswalk (our only source of regional-council membership) or the 2022 census population file. `population` is null for these two.
- Name matching required normalization for: trailing `*` footnote markers in the population file (e.g. `בנימינה-גבעת עדה*`), inconsistent spacing around hyphens (`אל-בטוף` vs `אל - בטוף`), handled by `normalize_name()` in `pipeline/build_authority_registry.py`.
- **Tzur Hadassah** (צור הדסה) appears in `table4` as its own standalone authority, but the 2019 cluster crosswalk still lists it as a village under Mateh Yehuda regional council (it became administratively independent since ~2022). Resolved by prioritizing direct name matches over council-aggregated population — but this is a reminder that the crosswalk is a 2019 snapshot and may misclassify other authorities that changed status in 2020-2024. Not exhaustively checked for other such cases.

## Fields not yet sourced (null in current build)

- **district (מחוז)**: no source found yet that maps authority → district. Checked: data.gov.il local_authorities.csv (no district column), 2022 census population file (no district column), CKAN searches for a dedicated district-mapping dataset (none found). May be derivable from CBS table1/table2 (organized by מחוז/נפה) in a future pass — not yet attempted.
- **socioeconomic_cluster**: the only cluster dataset found (`socioeconomic_cluster_2019.csv`) covers only villages within regional councils (995 rows, 54 councils) — it has no entries for standalone cities/local councils, which are most of what the dashboard needs (Bat Yam, Holon, Tel Aviv, etc. are all absent). Rather than ship a column that's populated only for a minority, non-representative subset of authorities, it's left entirely null pending discovery of CBS's actual comprehensive socioeconomic characterization ("אפיון יישובים לפי הרמה החברתית-כלכלית"), which does not appear to be on data.gov.il as a clean file. The "פרופיל כלל ארצי" PDF (checked 2026-07-19) turned out to be a national one-page summary infographic, not a per-authority table — dead end.
- **pct_other_recovery**: `table4` only gives a combined "transferred to recycling and recovery" figure — recycling and other-recovery (e.g. waste-to-energy) are not split out in this table. Would require parsing `table1`/`table2` (organized by separation method / material) to attempt a split — not yet attempted.
