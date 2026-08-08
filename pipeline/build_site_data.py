"""Build site/data/waste.json from data/processed/waste.csv + CBS national totals.

Run with: uv run --with pandas --with xlrd python3 pipeline/build_site_data.py
"""

import json
import re
from datetime import date, timezone, datetime

import pandas as pd

from parse_cbs_waste import parse_national_totals, parse_national_material_breakdown, MATERIAL_KEYS

WASTE_CSV = "data/processed/waste.csv"
OUT_PATH = "site/data/waste.json"

POPULATION_BUCKETS = [
    (0, 5_000, "under_5k"),
    (5_000, 20_000, "5k_20k"),
    (20_000, 50_000, "20k_50k"),
    (50_000, 100_000, "50k_100k"),
    (100_000, float("inf"), "over_100k"),
]


def slugify(name_en: str) -> str:
    s = name_en.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def population_bucket(pop):
    if pop is None or pd.isna(pop):
        return None
    for lo, hi, key in POPULATION_BUCKETS:
        if lo <= pop < hi:
            return key
    return None


def build_site_data():
    df = pd.read_csv(WASTE_CSV)
    national = parse_national_totals()

    years = sorted(df["year"].unique().tolist())

    authorities = []
    for (name_he, name_en), group in df.groupby(
        ["authority_name_he", "authority_name_en"], dropna=False
    ):
        group = group.sort_values("year")
        latest = group.iloc[-1]
        pop = latest["population"] if pd.notna(latest["population"]) else None

        year_data = {}
        prev_pct = None
        for _, r in group.iterrows():
            pct = r["pct_recycled"] if pd.notna(r["pct_recycled"]) else None
            year_data[str(int(r["year"]))] = {
                "reported": bool(r["reported"]),
                "total_waste_tons": None if pd.isna(r["total_waste_tons"]) else round(r["total_waste_tons"], 1),
                "kg_per_capita_day": None if pd.isna(r["kg_per_capita_day"]) else round(r["kg_per_capita_day"], 3),
                "pct_recycled": None if pct is None else round(pct, 2),
                "pct_landfilled": None if pd.isna(r["pct_landfilled"]) else round(r["pct_landfilled"], 2),
                "trend_vs_prev_year": None if (pct is None or prev_pct is None) else round(pct - prev_pct, 2),
            }
            if pct is not None:
                prev_pct = pct

        authorities.append(
            {
                "slug": slugify(name_en),
                "name_he": name_he,
                "name_en": name_en,
                "authority_id": None if pd.isna(latest["authority_id"]) else int(latest["authority_id"]),
                "population": None if pop is None else int(pop),
                "population_bucket": population_bucket(pop),
                "years": year_data,
            }
        )

    national_data = {}
    for _, r in national.iterrows():
        national_data[str(int(r["year"]))] = {
            "total_waste_tons": round(r["total_waste_tons"], 1),
            "pct_recycled": round(r["pct_recycled"], 2),
            "pct_landfilled": round(r["pct_landfilled"], 2),
            "kg_per_capita_day": round(r["kg_per_capita_day"], 3),
        }

    materials = parse_national_material_breakdown()
    material_data = {}
    for _, r in materials.iterrows():
        material_data[str(int(r["year"]))] = {k: round(r[k], 1) for k in MATERIAL_KEYS}

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "years": years,
        "targets_2030": {"pct_recycled": 54, "pct_landfilled": 20},
        "national": national_data,
        "national_materials": material_data,
        "authorities": sorted(authorities, key=lambda a: a["name_en"]),
    }
    return payload


if __name__ == "__main__":
    import os

    payload = build_site_data()
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=None)
    print(f"wrote {OUT_PATH}: {len(payload['authorities'])} authorities, years {payload['years'][0]}-{payload['years'][-1]}")
