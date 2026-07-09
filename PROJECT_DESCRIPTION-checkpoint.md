# Spatial Compliance Analysis of Kigali's Built Environment Against the 2050 Master Plan Using Satellite-Derived Building Footprints

## Group Information

- **Group Number:** [TO BE ASSIGNED]
- **Members:** [NAMES HERE]
- **Submission Date:** May 2026

---

## 1. Project Title

**Spatial Compliance Analysis of Kigali's Built Environment Against the 2050 Master Plan Using Satellite-Derived Building Footprints**

## 2. Problem Statement

Kigali is one of Africa's fastest-urbanizing cities, but rapid growth often outpaces formal planning and enforcement. Buildings are constructed in protected wetlands, on steep slopes, in agricultural zones, and outside registered parcels — yet no comprehensive, up-to-date spatial assessment exists to quantify the gap between the Master Plan and the built reality on the ground.

Traditional compliance monitoring relies on manual field surveys that cannot scale to a city of 479,000+ structures. This project addresses that gap by combining freely available satellite-derived building data with official planning datasets to produce a city-wide compliance assessment.

## 3. Research Questions

1. How well does Kigali's existing built environment align with the registered cadastral parcel system?
2. What proportion of buildings fall within zones where construction conflicts with the Kigali Master Plan (2050)?
3. Where are the most critical conflict hotspots by sector and district?
4. Can density-based clustering detect potential informal settlements from building footprint patterns?
5. What is the spatial distribution of parcel overcrowding and underutilization across the city?

## 4. Objectives

**Main Objective:** Assess the spatial compliance of Kigali's built environment against its Master Plan using GIS overlay analysis and machine learning clustering.

**Specific Objectives:**
- Classify all buildings by parcel registration status (aligned, unregistered, wetland conflict)
- Overlay buildings against the 29 zoning designations to quantify compliance vs. conflict
- Map conflict rates at the sector level to identify priority enforcement areas
- Detect informal settlement clusters using DBSCAN on unregistered building footprints
- Analyze parcel utilization to identify overcrowded and underused areas

## 5. Study Area

**Kigali City, Rwanda** — covering all three districts:
- **Gasabo** (northern, largest by area, most peri-urban)
- **Kicukiro** (southern, most suburban)
- **Nyarugenge** (central, contains the CBD)

The analysis covers 37 sectors across the full urban and peri-urban extent of Kigali.

## 6. Data Sources

| Dataset | Source | Records | Description |
|---------|--------|---------|-------------|
| Building Footprints | Google Open Buildings v3 | 479,342 | ML-derived polygons from high-res satellite imagery, with area and confidence scores |
| Registered Parcels | Rwanda Land Management Authority (RLMA) | 550,842 | Official cadastral dataset with admin boundaries, parcel areas, and wetland flags |
| Proposed Zoning Plan | Kigali Master Plan 2050 (City of Kigali) | 8,180 polygons | 29 zone types: residential, commercial, industrial, protected areas, wetlands, transport |

## 7. Methodology

### 7.1 Data Preparation
- Load and clean all geometries (fix invalid polygons using buffer(0))
- Project to UTM Zone 36S (EPSG:32736) for accurate distance/area calculations
- Clip building footprints to Kigali boundary derived from dissolved parcels
- Remove outlier parcels (>99.9th percentile distance from centroid)

### 7.2 Parcel Registration Classification
- Buffer all parcels by 3 meters to account for GPS/digitization misalignment
- Spatial join (intersects) of buildings to parcels
- Classify each building as:
  - **Aligned:** within a registered parcel (no wetland flag)
  - **Wetland Conflict:** within a parcel flagged as wetland
  - **Unregistered:** outside any registered parcel
- Assign admin areas to unregistered buildings via nearest-parcel join

### 7.3 Zoning Compliance Overlay
- Spatial join of buildings against the 29 zoning designations
- Categorize each building's zone as:
  - **Compatible:** residential, commercial, industrial, public facilities
  - **Open Space Conflict:** parks, agriculture, eco-tourism zones
  - **Forest/Slopes Conflict:** forest zones, steep slopes (>30%)
  - **Wetland Conflict:** rehabilitation, conservation, sustainable exploitation zones
  - **Transportation Conflict:** road/transport corridors

### 7.4 Informal Settlement Detection
- Filter small unregistered buildings (<100 m²)
- Apply DBSCAN clustering (eps=50m, min_samples=10)
- Characterize clusters by building count, mean footprint area, and location

### 7.5 Parcel Utilization Analysis
- For each parcel, compute total building footprint area / parcel area
- Classify as overcrowded (>80%), normal, or underused (<10%)
- Aggregate by sector for spatial pattern analysis

### 7.6 Spatial Visualization
- Sector-level choropleth maps (conflict rate, utilization)
- Side-by-side plan vs. reality comparison
- Wetland encroachment focus maps
- Informal settlement close-up panels
- Building density hexbin maps
- Interactive web maps (Folium) with layer controls

## 8. Tools and Technologies

- **Python 3.11** — primary analysis language
- **GeoPandas + Shapely** — spatial joins, overlay, geometry operations
- **Scikit-learn (DBSCAN)** — density-based clustering for informal settlement detection
- **Matplotlib + Contextily** — publication-quality static maps with basemap tiles
- **Folium** — interactive HTML maps with satellite imagery
- **Jupyter Notebook** — reproducible analysis workflow

## 9. Key Findings

| Finding | Value |
|---------|-------|
| Buildings analyzed | 479,342 |
| Parcel alignment rate | 98.0% (469,531 aligned) |
| Unregistered buildings | 7,379 (1.5%) |
| Wetland parcel conflicts | 2,432 (0.5%) |
| Zoning-compatible buildings | 77.0% (368,968) |
| Buildings in conflict zones | 105,768 (22.1%) |
| Top conflict type | Open Space/Agriculture (68,214) |
| Informal settlement clusters | 59 clusters, 2,888 buildings |
| Overcrowded parcels (>80%) | 120,532 |
| Underused parcels (<10%) | 57,497 |

## 10. Expected Outputs

1. Classified building dataset (GeoPackage) with parcel and zoning compliance attributes
2. Sector-level compliance summary statistics (CSV)
3. 15+ publication-quality maps (static PNG/PDF)
4. Interactive web maps (HTML) for stakeholder exploration
5. 19-slide presentation with maps, charts, and recommendations
6. Reproducible Jupyter notebook with full analysis pipeline

## 11. Significance

This project demonstrates that **freely available satellite-derived data** (Google Open Buildings) combined with **open government data** can produce actionable urban compliance analytics at city scale. The methodology is:
- **Scalable** — applicable to any Rwandan city with cadastral + zoning data
- **Reproducible** — fully scripted pipeline, no manual digitization required
- **Actionable** — identifies specific sectors and clusters for enforcement priority

The findings directly support Rwanda's urbanization goals by quantifying where planning intervention is most needed.

## 12. Project Structure

```
jn/
├── notebooks/
│   ├── analyze.ipynb              # Main analysis notebook
│   └── explore_open_buildings.ipynb
├── scripts/
│   ├── generate_maps.py           # 6 advanced map generation
│   ├── analyze.py
│   ├── extract_data.py
│   └── download_*.py
├── data/
│   ├── raw/                       # Original datasets
│   ├── processed/                 # Classified/zoned buildings
│   ├── output/                    # Summary CSVs
│   └── figures/                   # All maps and charts
├── presentation/
│   ├── generate_presentation.js   # PPTX generation script
│   └── Kigali_Master_Plan_Analysis.pptx
└── PROJECT_DESCRIPTION.md         # This file
```
