"""Build a population registry: one row per local authority (matching table4's
granularity), with total population.

Standalone authorities (cities, local councils) appear directly in the CBS 2022
census population-by-locality file. Regional councils do NOT appear there as a
single row -- only their constituent villages do -- so we aggregate villages up
to council level using the village->council crosswalk from the socioeconomic
cluster file (the only source we have of that mapping).

Socioeconomic cluster is NOT included here: the only cluster file available
covers regional-council villages only, with no equivalent for standalone
cities/local councils, so it would be a misleading partial column. Documented
as a known gap in data/SOURCES.md.
"""

import re

import pandas as pd

POP_PATH = "data/raw/cbs_population_socioeconomic/population_by_locality_2022.csv"
CLUSTER_PATH = "data/raw/cbs_population_socioeconomic/socioeconomic_cluster_2019.csv"


def normalize_name(name: str) -> str:
    """Normalize Hebrew authority names for matching across CBS sources.

    Handles known variance: trailing footnote markers (*), inconsistent
    spacing around hyphens, and stray whitespace.
    """
    s = str(name).strip()
    s = s.rstrip("*").strip()
    s = re.sub(r"\s*-\s*", "-", s)
    s = re.sub(r"\s+", " ", s)
    return s


def _parse_population(val):
    if pd.isna(val):
        return None
    s = str(val).strip().replace(",", "")
    if s in ("", "-"):
        return None
    try:
        return int(float(s))
    except ValueError:
        return None


def build_population_registry() -> pd.DataFrame:
    pop = pd.read_csv(POP_PATH)
    pop.columns = [c.strip() for c in pop.columns]
    pop = pop[pd.to_numeric(pop["LocalityCode"], errors="coerce").notna()].copy()
    pop["LocalityCode"] = pop["LocalityCode"].astype(int)
    pop["population"] = pop["Total_Population"].apply(_parse_population)
    pop["name_norm"] = pop["LocNameHeb"].apply(normalize_name)

    cluster = pd.read_csv(CLUSTER_PATH)
    cluster = cluster.loc[:, ~cluster.columns.str.match(r"Unnamed")]
    cluster.columns = [c.strip() for c in cluster.columns]
    cluster["LOCALITY SYMBOL"] = cluster["LOCALITY SYMBOL"].astype(int)
    cluster["council_name_norm"] = cluster["HEBREW NAME OF REGIONAL COUNCIL"].apply(
        normalize_name
    )

    village_to_council = cluster.set_index("LOCALITY SYMBOL")[
        "council_name_norm"
    ].to_dict()
    pop["regional_council_he"] = pop["LocalityCode"].map(village_to_council)

    # Direct name matches take priority: covers standalone cities/local councils,
    # and also authorities that seceded from a regional council since the 2019
    # cluster crosswalk was published (e.g. Tzur Hadassah, independent from
    # Mateh Yehuda regional council as of ~2022, but the crosswalk still lists
    # it as a Mateh Yehuda village) -- their own direct population row wins
    # over stale council-membership aggregation. authority_id (CBS locality
    # code) is only meaningful for these standalone/direct matches -- a
    # regional council itself has no single locality code, only its member
    # villages do, so aggregated council rows get a null authority_id.
    direct = pop.groupby("name_norm", as_index=False).agg(
        population=("population", "sum"), authority_id=("LocalityCode", "first")
    )
    direct = direct.rename(columns={"name_norm": "authority_name_he"})

    # regional councils: sum constituent villages' population (fallback only,
    # used for names with no direct standalone entry)
    council_agg = (
        pop[pop["regional_council_he"].notna()]
        .groupby("regional_council_he", as_index=False)["population"]
        .sum(min_count=1)
        .rename(columns={"regional_council_he": "authority_name_he"})
    )
    council_agg["authority_id"] = None

    direct_names = set(direct["authority_name_he"])
    council_only = council_agg[~council_agg["authority_name_he"].isin(direct_names)]

    registry = pd.concat([direct, council_only], ignore_index=True)
    registry = registry.drop_duplicates(subset="authority_name_he")
    return registry


if __name__ == "__main__":
    reg = build_population_registry()
    print(reg.shape)
    print(reg[reg["authority_name_he"].str.contains("שער הנגב|צור הדסה", na=False, regex=True)].to_string())
