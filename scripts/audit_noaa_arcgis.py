"""
NOAA/OBIS Real-Data Audit for April 2017 Mini-Split
Queries:
1. NOAA ArcGIS NARW FeatureServer (layers 0 and 1) - schema + April 2017 + bounding box
2. OBIS occurrence API - taxon 137094 (Eubalaena glacialis) + April 2017 + study region
3. OBIS-SEAMAP dataset search for NARWSS records
"""
import requests
import pandas as pd
import json
import warnings
warnings.filterwarnings("ignore")

BASE_ARCGIS = "https://services2.arcgis.com/C8EMgrsFcRFL6LrL/arcgis/rest/services/North_Atlantic_Right_Whale_Aerial_Survey/FeatureServer"

# Study region: 41.0-43.5N, -71.5 to -68.5W
STUDY_BBOX = {
    "xmin": -71.5,
    "ymin": 41.0,
    "xmax": -68.5,
    "ymax": 43.5
}

# April 2017 epoch milliseconds (ArcGIS uses Unix ms)
# Note: ArcGIS date filters need the epoch ms or ISO string depending on endpoint config
APRIL_START = "2017-04-01T00:00:00Z"
APRIL_END   = "2017-04-30T23:59:59Z"

def audit_arcgis_layer(layer_id):
    """Get schema metadata for a FeatureServer layer."""
    url = f"{BASE_ARCGIS}/{layer_id}?f=json"
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    print(f"\n=== Layer {layer_id}: {data.get('name')} ===")
    print(f"Geometry Type    : {data.get('geometryType')}")
    print(f"Feature Count    : {data.get('maxRecordCount', 'unknown')} (server max per page)")
    print(f"Has Attachments  : {data.get('hasAttachments')}")

    print("\nFields:")
    fields = data.get('fields', [])
    for f in fields:
        print(f"  {f['name']:40s} {f['type']}")
    return fields

def get_total_count(layer_id, where="1=1", geometry=None):
    """Get total record count for a given where clause and optional geometry."""
    url = f"{BASE_ARCGIS}/{layer_id}/query"
    params = {
        "where": where,
        "returnCountOnly": True,
        "f": "json"
    }
    if geometry:
        params["geometry"] = json.dumps(geometry)
        params["geometryType"] = "esriGeometryEnvelope"
        params["spatialRel"] = "esriSpatialRelIntersects"
        params["inSR"] = "4326"

    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json().get("count", "error")

def get_sample_records(layer_id, where="1=1", geometry=None, n=5):
    """Return sample records with full attributes."""
    url = f"{BASE_ARCGIS}/{layer_id}/query"
    params = {
        "where": where,
        "outFields": "*",
        "returnGeometry": True,
        "resultRecordCount": n,
        "f": "json"
    }
    if geometry:
        params["geometry"] = json.dumps(geometry)
        params["geometryType"] = "esriGeometryEnvelope"
        params["spatialRel"] = "esriSpatialRelIntersects"
        params["inSR"] = "4326"
        params["outSR"] = "4326"

    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    features = data.get("features", [])
    if not features:
        print(f"  No features returned for layer {layer_id}")
        return None

    rows = []
    for feat in features:
        row = feat.get("attributes", {})
        geom = feat.get("geometry", {})
        # For polylines, capture path count
        if "paths" in geom:
            row["_geom_path_count"] = len(geom["paths"])
            row["_geom_point_count"] = sum(len(p) for p in geom["paths"])
        elif "x" in geom and "y" in geom:
            row["_geom_lon"] = geom["x"]
            row["_geom_lat"] = geom["y"]
        rows.append(row)

    df = pd.DataFrame(rows)
    return df

def audit_obis_narw_april2017():
    """Query OBIS v3 for Eubalaena glacialis in study region, April 2017."""
    print("\n=== OBIS Occurrence Query (taxon 137094) ===")
    url = "https://api.obis.org/v3/occurrence"
    wkt = "POLYGON((-71.5 41.0, -68.5 41.0, -68.5 43.5, -71.5 43.5, -71.5 41.0))"
    params = {
        "taxonid": 137094,
        "geometry": wkt,
        "startdate": "2017-04-01",
        "enddate": "2017-04-30",
        "size": 1000
    }
    resp = requests.get(url, params=params, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    records = data.get("results", [])
    total = data.get("total", "unknown")
    print(f"Total records (API): {total}")
    print(f"Records returned   : {len(records)}")
    if records:
        df = pd.DataFrame(records)
        print(f"Columns available  : {list(df.columns)}")
        effort_cols = [c for c in df.columns if any(kw in c.lower() for kw in
                       ['effort', 'track', 'survey', 'distance', 'transect',
                        'platform', 'samplesize', 'samplingprotocol'])]
        print(f"Effort-related cols: {effort_cols}")
        print(f"basisOfRecord distribution:")
        if 'basisOfRecord' in df.columns:
            print(df['basisOfRecord'].value_counts().to_string())
        print(f"datasetName distribution:")
        if 'datasetName' in df.columns:
            print(df['datasetName'].value_counts().to_string())
    return records

def audit_obis_datasets():
    """Search OBIS dataset registry for NARWSS/NEFSC datasets with effort data."""
    print("\n=== OBIS Dataset Search (NARWSS + NEFSC) ===")
    for q in ["NARWSS North Atlantic Right Whale Sighting Survey",
              "AMAPPS Northeast Aerial"]:
        url = "https://api.obis.org/v3/dataset"
        resp = requests.get(url, params={"q": q, "size": 10}, timeout=15)
        if resp.status_code == 200:
            results = resp.json().get("results", [])
            print(f"\nQuery: '{q}' -> {len(results)} datasets:")
            for d in results:
                print(f"  [{d.get('id','')}] {d.get('title','')}")

def check_date_fields_and_filter(layer_id, fields):
    """Check which fields are date types and attempt to filter by April 2017."""
    date_fields = [f['name'] for f in fields if 'Date' in f['type'] or 'TIME' in f['name'].upper()
                   or 'DATE' in f['name'].upper() or 'YEAR' in f['name'].upper()]
    print(f"\nDate/Time fields in layer {layer_id}: {date_fields}")
    return date_fields

if __name__ == "__main__":
    print("=" * 60)
    print("NOAA/OBIS Real Data Audit — April 2017 Mini-Split")
    print("Study region: 41.0-43.5N, -71.5 to -68.5W")
    print("=" * 60)

    # --- ARCGIS LAYER 0: SMIT_NARW_LINES ---
    fields_0 = audit_arcgis_layer(0)
    date_fields_0 = check_date_fields_and_filter(0, fields_0)

    # Total record count (all time)
    total_all = get_total_count(0)
    print(f"\nLayer 0 total records (all time): {total_all}")

    # Record count inside study region (all time)
    bbox_geom = {"xmin": STUDY_BBOX["xmin"], "ymin": STUDY_BBOX["ymin"],
                 "xmax": STUDY_BBOX["xmax"], "ymax": STUDY_BBOX["ymax"]}
    total_region = get_total_count(0, geometry=bbox_geom)
    print(f"Layer 0 records inside study region (all time): {total_region}")

    # Sample records inside study region
    print("\nSample records (Layer 0, study region):")
    df_sample = get_sample_records(0, geometry=bbox_geom, n=5)
    if df_sample is not None:
        print(df_sample.to_string())

    # Try date filtering if date fields exist
    if date_fields_0:
        df_field = date_fields_0[0]
        # ArcGIS SQL-style date filter
        where_april = f"{df_field} >= DATE '2017-04-01' AND {df_field} <= DATE '2017-04-30'"
        c_april = get_total_count(0, where=where_april, geometry=bbox_geom)
        print(f"\nLayer 0 records April 2017 + study region: {c_april}")

    # --- ARCGIS LAYER 1: SMIT_NARW_STRATA ---
    print("\n")
    fields_1 = audit_arcgis_layer(1)
    total_all_1 = get_total_count(1)
    print(f"\nLayer 1 total records (all time): {total_all_1}")
    total_region_1 = get_total_count(1, geometry=bbox_geom)
    print(f"Layer 1 records inside study region: {total_region_1}")
    df_sample_1 = get_sample_records(1, geometry=bbox_geom, n=3)
    if df_sample_1 is not None:
        print("\nSample records (Layer 1, study region):")
        print(df_sample_1.to_string())

    # --- OBIS OCCURRENCE + DATASET AUDIT ---
    audit_obis_narw_april2017()
    audit_obis_datasets()
