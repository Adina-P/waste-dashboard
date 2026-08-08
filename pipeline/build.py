"""Build data/processed/waste.csv from all raw sources.

Run with: uv run --with pandas --with xlrd python3 pipeline/build.py
"""

import pandas as pd

from build_authority_registry import build_population_registry, normalize_name
from parse_cbs_waste import parse_cbs_waste_by_authority

OUT_PATH = "data/processed/waste.csv"

COLUMN_ORDER = [
    "authority_id",
    "authority_name_he",
    "authority_name_en",
    "district",
    "population",
    "socioeconomic_cluster",
    "year",
    "total_waste_tons",
    "kg_per_capita_day",
    "pct_recycled",
    "pct_landfilled",
    "pct_other_recovery",
    "reported",
    "source_url",
    "source_name",
]


def build() -> pd.DataFrame:
    waste = parse_cbs_waste_by_authority()
    registry = build_population_registry()

    waste["authority_name_he"] = waste["authority_name_he"].apply(normalize_name)

    df = waste.merge(registry, on="authority_name_he", how="left")

    df["pct_landfilled"] = (df["tons_landfilled"] / df["total_waste_tons"]) * 100

    # Known gaps, not yet resolved from any available source (see data/SOURCES.md
    # and data/CONFLICTS.md): district, and a clean recycling-vs-other-recovery
    # split (table4 only gives a combined "recycling and recovery" figure).
    df["district"] = None
    df["socioeconomic_cluster"] = None
    df["pct_other_recovery"] = None

    for col in COLUMN_ORDER:
        if col not in df.columns:
            df[col] = None

    return df[COLUMN_ORDER].sort_values(["year", "authority_name_he"])


if __name__ == "__main__":
    df = build()
    df.to_csv(OUT_PATH, index=False)
    print(f"wrote {OUT_PATH}: {df.shape}")
    print(f"authority_id coverage: {df['authority_id'].notna().mean():.1%}")
    print(f"population coverage: {df['population'].notna().mean():.1%}")
    print(df[df['year'] == 2024].head(10).to_string())
