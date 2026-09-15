import os

def generate_feasibility_report():
    report = """# Data Feasibility Audit

## Study Region Validation
**Region**: Gulf of Maine & Cape Cod Bay (41.0°N–43.5°N, -71.5°W–-68.5°W)
**Justification**: This region contains critical foraging habitat (Cape Cod Bay) and major shipping lanes (approach to Boston). The spatial extent is roughly 250km x 250km, which matches our 64x64 grid at ~4km resolution.

## 1. Historical AIS Vessel Traffic (NOAA Marine Cadastre)
*   **Spatial Coverage**: Fully covers the study region (US EEZ).
*   **Temporal Coverage**: 2015–Present.
*   **Resolution**: Broadcast frequency (seconds to minutes).
*   **Missingness**: Low for Class A vessels; some Class B gaps.
*   **Access/License**: Public Domain. Direct bulk ZIP download.
*   **Volume**: ~1-2 GB per month for the East Coast.
*   **Synchronization**: Needs resampling to 6-hour grids and MMSI trajectory interpolation.
*   **Status**: **Mandatory (Accessibly Available)**

## 2. Acoustic Detections (WHOI / NOAA NEFSC)
*   **Spatial Coverage**: Point locations (gliders and moored buoys) in CCB and Stellwagen.
*   **Temporal Coverage**: Intermittent deployments, heavy in winter/spring. 2015-present.
*   **Resolution**: Exact timestamp of upcalls.
*   **Missingness**: High spatial sparsity. Dependent on buoy deployment.
*   **Access/License**: Public/Request-based.
*   **Volume**: < 100 MB (metadata/logs).
*   **Synchronization**: Bin into 6-hour grid cells.
*   **Status**: **Mandatory (Access Pending for full resolution, public feed available)**

## 3. Visual Sightings (OBIS-SEAMAP / WhaleMap)
*   **Spatial Coverage**: Survey transects across the region.
*   **Temporal Coverage**: 2010–Present.
*   **Resolution**: Exact timestamp and lat/lon.
*   **Missingness**: Massive effort bias. Zero flights in bad weather or at night.
*   **Access/License**: Public (cite providers).
*   **Volume**: < 50 MB.
*   **Status**: **Mandatory (Accessibly Available)**

## 4. Ocean Surface Currents (CMEMS GLORYS12V1 or OSCAR)
*   **Spatial Coverage**: Global.
*   **Temporal Coverage**: 1993–Present.
*   **Resolution**: 1/12° (approx 8km), Daily.
*   **Missingness**: None over water.
*   **Access/License**: Copernicus Marine (Free registration).
*   **Volume**: ~500 MB per year for this crop.
*   **Synchronization**: Spatiotemporal interpolation to 0.05° 6-hourly grid.
*   **Status**: **Mandatory (Accessibly Available)**

## 5. Wind Fields (ERA5)
*   **Spatial Coverage**: Global.
*   **Temporal Coverage**: 1940–Present.
*   **Resolution**: 0.25° (approx 30km), Hourly.
*   **Missingness**: None.
*   **Access/License**: Copernicus Climate Data Store (Free).
*   **Volume**: ~100 MB per year for this crop.
*   **Synchronization**: Spatiotemporal interpolation to 0.05° 6-hourly grid.
*   **Status**: **Mandatory (Accessibly Available)**

## 6. Bathymetry (GEBCO)
*   **Spatial Coverage**: Global.
*   **Temporal Coverage**: Static.
*   **Resolution**: 15 arc-second (~500m).
*   **Missingness**: None.
*   **Status**: **Mandatory (Accessibly Available)**

## 7. Chlorophyll-a (MODIS-Aqua / VIIRS)
*   **Spatial Coverage**: Global.
*   **Temporal Coverage**: 2002-Present.
*   **Resolution**: 4km, Daily.
*   **Missingness**: HIGH due to cloud cover. Often 60-80% missing pixels daily.
*   **Synchronization**: Requires 8-day rolling composites or spatial interpolation to fill gaps.
*   **Status**: **Optional Enrichment**

## Synthesis & Common Historical Period
*   **Common Period Identified**: **2017-01-01 to 2021-12-31**
    *   This 5-year block avoids recent lags in AIS/Acoustic archiving and predates 2024 changes in some satellite products.
    *   Proposed Splits:
        *   Train: 2017, 2018, 2019
        *   Val: 2020
        *   Test: 2021
*   **Feasibility Conclusion**: The region and timeframe are data-rich enough for v1. The high density of visual sightings + continuous acoustic buoy presence in Cape Cod Bay during spring provides sufficient positive labels. 
"""
    
    os.makedirs('data', exist_ok=True)
    with open('data/FEASIBILITY.md', 'w', encoding='utf-8') as f:
        f.write(report)
    print("Wrote data/FEASIBILITY.md")

if __name__ == "__main__":
    generate_feasibility_report()
