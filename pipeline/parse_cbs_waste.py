"""Parse CBS 'table4' (waste by treatment method and local authority, 2014-2024) into tidy rows.

Source: data/raw/cbs_waste_2014_2024/table4_by_treatment_and_authority_2014-2024.xls
One sheet per year. Layout per sheet: rows 0-12 are title/header boilerplate,
row 13 is the national TOTAL row, data rows follow one per authority, and the
sheet ends with footnote text rows ("Data based on: ...").
"""

import pandas as pd

RAW_PATH = "data/raw/cbs_waste_2014_2024/table4_by_treatment_and_authority_2014-2024.xls"
SOURCE_URL = "https://www.cbs.gov.il/he/publications/Pages/2019/פסולת-שנאספה-ברשויות-המקומיות-2014-2017.aspx"
SOURCE_NAME = "CBS - Household and Commercial Waste Collected, by Type of Treatment and Local Authority"


def _to_float(val):
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    if s in ("", "..", "-", "nan"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def parse_cbs_waste_by_authority() -> pd.DataFrame:
    xls = pd.ExcelFile(RAW_PATH)
    rows = []
    for sheet in xls.sheet_names:
        year = int(sheet)
        df = xls.parse(sheet, header=None)
        # data rows start at index 14 (index 13 is the national TOTAL row)
        for _, r in df.iloc[14:].iterrows():
            name_en = r[0]
            if not isinstance(name_en, str) or name_en.strip() == "":
                continue
            if name_en.strip().lower().startswith("data based on"):
                break  # footnote block reached, end of data rows
            rows.append(
                {
                    "year": year,
                    "authority_name_en": name_en.strip(),
                    "authority_name_he": str(r[6]).strip() if pd.notna(r[6]) else None,
                    "pct_recycled": _to_float(r[1]),
                    "tons_recycled_recovery": _to_float(r[2]),
                    "tons_landfilled": _to_float(r[3]),
                    "kg_per_capita_day": _to_float(r[4]),
                    "total_waste_tons": _to_float(r[5]),
                    "source_url": SOURCE_URL,
                    "source_name": SOURCE_NAME,
                }
            )
    out = pd.DataFrame(rows)
    out["reported"] = out["total_waste_tons"].notna()
    return out


def parse_national_totals() -> pd.DataFrame:
    """CBS's own official national TOTAL row per year (row index 13 of each sheet).

    Use this for national-level figures, not a sum of per-authority rows --
    see data/CONFLICTS.md: CBS's total includes waste attributable to
    non-reporting/unallocated authorities that never appear as individual rows,
    so it runs ~7-8% higher than summing the visible per-authority data.
    """
    xls = pd.ExcelFile(RAW_PATH)
    rows = []
    for sheet in xls.sheet_names:
        year = int(sheet)
        df = xls.parse(sheet, header=None)
        r = df.iloc[13]
        rows.append(
            {
                "year": year,
                "pct_recycled": _to_float(r[1]),
                "tons_recycled_recovery": _to_float(r[2]),
                "tons_landfilled": _to_float(r[3]),
                "kg_per_capita_day": _to_float(r[4]),
                "total_waste_tons": _to_float(r[5]),
            }
        )
    out = pd.DataFrame(rows).sort_values("year").reset_index(drop=True)
    out["pct_landfilled"] = out["tons_landfilled"] / out["total_waste_tons"] * 100
    return out


MATERIAL_TABLE_PATH = "data/raw/cbs_waste_2014_2024/table2_recycled_materials_by_district_2014-2024.xls"
MATERIAL_COLUMNS_HE = ["אחר", "גזם", "חומר אורגני", "זכוכית", "מתכת", "פלסטיק", "קרטון", "נייר"]
MATERIAL_KEYS = ["other", "yard_waste", "organic", "glass", "metal", "plastic", "cardboard", "paper"]


def parse_national_material_breakdown() -> pd.DataFrame:
    """National-level (not per-authority) breakdown of recycled/recovered tons by
    material, from CBS table2 (organized by district/sub-district -- we use only
    the national TOTAL row per year, row index 10 of each sheet). Column order
    is stable across 2014-2024 sheets: other, yard waste, organic material,
    glass, metal, plastic, cardboard, paper.
    """
    xls = pd.ExcelFile(MATERIAL_TABLE_PATH)
    rows = []
    for sheet in xls.sheet_names:
        year = int(sheet)
        df = xls.parse(sheet, header=None)
        total_row = df.iloc[10]
        record = {"year": year}
        for i, key in enumerate(MATERIAL_KEYS):
            record[key] = _to_float(total_row[i + 1])
        rows.append(record)
    return pd.DataFrame(rows).sort_values("year").reset_index(drop=True)


if __name__ == "__main__":
    df = parse_cbs_waste_by_authority()
    print(df.shape)
    print(df.head(10).to_string())
    print("years:", sorted(df["year"].unique()))
    print("reported counts by year:")
    print(df.groupby("year")["reported"].agg(["sum", "count"]))
