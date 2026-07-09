"""
Kigali Master Plan vs Open Buildings: Spatial Overlay Analysis
==============================================================
Classifies every Open Buildings footprint by its relationship to the
master plan parcels:
  - aligned:      building is within a registered parcel (no wetland)
  - wetland:      building overlaps wetland-designated land
  - unregistered: building falls outside any registered parcel

Usage:
  python analyze.py

Input:
  kigali_masterplan_data/geojson/Kigali_Parcels.geojson
  kigali_masterplan_data/open_buildings/open_buildings_kigali.gpkg

Output:
  kigali_masterplan_data/analysis/buildings_classified.gpkg
  kigali_masterplan_data/analysis/summary_by_district.csv
  kigali_masterplan_data/analysis/summary_by_sector.csv
  kigali_masterplan_data/analysis/summary_by_cell.csv
"""

import geopandas as gpd
import pandas as pd
from pathlib import Path

# ─── CONFIG ──────────────────────────────────────────────────────────────────

PARCELS_PATH   = Path("kigali_masterplan_data/geojson/Kigali_Parcels.geojson")
BUILDINGS_PATH = Path("kigali_masterplan_data/open_buildings/open_buildings_kigali.gpkg")
OUTPUT_DIR     = Path("kigali_masterplan_data/analysis")

# Buffer in meters applied to parcels to reduce edge false positives
BUFFER_METERS  = 3

# CRS for accurate distance/area calculations (UTM Zone 36S for Rwanda)
UTM_CRS = "EPSG:32736"

# ─── LOAD DATA ───────────────────────────────────────────────────────────────

def load_parcels(path: Path) -> gpd.GeoDataFrame:
    print(f"[load] Reading parcels from {path}...")
    gdf = gpd.read_file(path)
    print(f"  {len(gdf)} parcels loaded")

    # Fix invalid geometries
    invalid = ~gdf.is_valid
    if invalid.sum() > 0:
        print(f"  Fixing {invalid.sum()} invalid geometries...")
        gdf.loc[invalid, "geometry"] = gdf.loc[invalid, "geometry"].buffer(0)

    return gdf


def load_buildings(path: Path) -> gpd.GeoDataFrame:
    print(f"[load] Reading buildings from {path}...")
    gdf = gpd.read_file(path)
    print(f"  {len(gdf)} buildings loaded")

    # Fix invalid geometries
    invalid = ~gdf.is_valid
    if invalid.sum() > 0:
        print(f"  Fixing {invalid.sum()} invalid geometries...")
        gdf.loc[invalid, "geometry"] = gdf.loc[invalid, "geometry"].buffer(0)

    return gdf


# ─── CLASSIFY BUILDINGS ─────────────────────────────────────────────────────

def classify_buildings(
    buildings: gpd.GeoDataFrame,
    parcels: gpd.GeoDataFrame,
    buffer_m: float,
) -> gpd.GeoDataFrame:
    """
    Classify each building based on its spatial relationship to parcels.
    """
    # Project to UTM for buffering
    print(f"[classify] Projecting to {UTM_CRS}...")
    buildings_utm = buildings.to_crs(UTM_CRS)
    parcels_utm = parcels.to_crs(UTM_CRS)

    # Buffer parcels slightly to account for spatial misalignment
    print(f"[classify] Buffering parcels by {buffer_m}m...")
    parcels_utm["geometry"] = parcels_utm.geometry.buffer(buffer_m)

    # Spatial join: find which buildings intersect any parcel
    print("[classify] Spatial join (this may take several minutes)...")
    joined = gpd.sjoin(
        buildings_utm,
        parcels_utm[["geometry", "area_in_wetland", "district", "sector", "cell"]],
        how="left",
        predicate="intersects",
    )

    # A building may match multiple parcels — deduplicate
    # Keep the first match (just need to know if it matched ANY parcel)
    joined = joined[~joined.index.duplicated(keep="first")]

    # Classify
    print("[classify] Classifying buildings...")
    has_parcel = joined["index_right"].notna()
    in_wetland = joined["area_in_wetland"].notna() & (joined["area_in_wetland"] > 0)

    joined["classification"] = "unregistered"
    joined.loc[has_parcel & ~in_wetland, "classification"] = "aligned"
    joined.loc[has_parcel & in_wetland, "classification"] = "wetland"

    # For unregistered buildings, we don't have admin info from the join.
    # Do a nearest-parcel join to assign them to the closest district/sector/cell.
    unregistered_mask = joined["classification"] == "unregistered"
    if unregistered_mask.sum() > 0:
        print(f"[classify] Assigning admin areas to {unregistered_mask.sum()} unregistered buildings...")
        unreg = joined.loc[unregistered_mask].copy()
        # Use sjoin_nearest to find closest parcel
        nearest = gpd.sjoin_nearest(
            unreg[["geometry"]],
            parcels_utm[["geometry", "district", "sector", "cell"]],
            how="left",
            max_distance=5000,  # 5 km max
        )
        nearest = nearest[~nearest.index.duplicated(keep="first")]
        joined.loc[unregistered_mask, "district"] = nearest["district"].values
        joined.loc[unregistered_mask, "sector"] = nearest["sector"].values
        joined.loc[unregistered_mask, "cell"] = nearest["cell"].values

    # Project back to WGS84 for output
    joined = joined.to_crs("EPSG:4326")

    # Clean up join columns
    joined = joined.drop(columns=["index_right"], errors="ignore")

    counts = joined["classification"].value_counts()
    print(f"\n[classify] Results:")
    for cls, count in counts.items():
        pct = count / len(joined) * 100
        print(f"  {cls:15s}: {count:>10,} ({pct:.1f}%)")

    return joined


# ─── STATISTICS ──────────────────────────────────────────────────────────────

def compute_summary(buildings: gpd.GeoDataFrame, group_col: str) -> pd.DataFrame:
    """Compute classification counts per administrative unit."""
    pivot = (
        buildings.groupby([group_col, "classification"])
        .size()
        .unstack(fill_value=0)
    )
    pivot["total"] = pivot.sum(axis=1)

    for col in ["aligned", "unregistered", "wetland"]:
        if col in pivot.columns:
            pivot[f"{col}_pct"] = (pivot[col] / pivot["total"] * 100).round(1)

    return pivot.sort_values("unregistered", ascending=False)


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load
    parcels = load_parcels(PARCELS_PATH)
    buildings = load_buildings(BUILDINGS_PATH)

    # Classify
    classified = classify_buildings(buildings, parcels, BUFFER_METERS)

    # Save classified buildings
    out_gpkg = OUTPUT_DIR / "buildings_classified.gpkg"
    print(f"\n[save] Saving classified buildings to {out_gpkg}...")
    classified.to_file(out_gpkg, driver="GPKG")
    print(f"  Done.")

    # Summaries
    for level in ["district", "sector", "cell"]:
        if level in classified.columns:
            summary = compute_summary(classified, level)
            out_csv = OUTPUT_DIR / f"summary_by_{level}.csv"
            summary.to_csv(out_csv)
            print(f"[summary] {level}: saved to {out_csv}")
            if level == "district":
                print(summary.to_string())

    print(f"\n{'='*60}")
    print("Analysis complete!")
    print(f"  Classified buildings: {out_gpkg}")
    print(f"  Summaries:           {OUTPUT_DIR}/summary_by_*.csv")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
