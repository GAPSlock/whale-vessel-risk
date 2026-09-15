"""
Part 2 of the real-data audit:
- Check AMAPPS datasets that appeared in prior OBIS query (ae75d50b Spring 2012 etc.)
- Check if they contain trackline/effort or only sighting occurrences
- Check OBIS-SEAMAP dataset IDs for 2017 NARWSS (URL pattern 102017)
- Probe WhaleMap API for NARW records April 2017
"""
import requests
import json

STUDY_WKT = "POLYGON((-71.5 41.0, -68.5 41.0, -68.5 43.5, -71.5 43.5, -71.5 41.0))"

def check_obis_dataset_records(dataset_id, label):
    """Check occurrence count and representative record from a specific OBIS dataset."""
    url = "https://api.obis.org/v3/occurrence"
    params = {
        "datasetid": dataset_id,
        "geometry": STUDY_WKT,
        "size": 5
    }
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        total = data.get("total", 0)
        results = data.get("results", [])
        
        print(f"\n[{label}] dataset={dataset_id}")
        print(f"  Total records in study region: {total}")
        if results:
            r = results[0]
            for key in ["basisOfRecord", "datasetName", "eventDate", "samplingProtocol",
                        "recordedBy", "institutionCode", "decimalLatitude",
                        "decimalLongitude", "occurrenceStatus"]:
                print(f"  {key}: {r.get(key, 'N/A')}")
    except Exception as e:
        print(f"  Error: {e}")

def check_obis_seamap_url(year):
    """Check OBIS-SEAMAP dataset metadata for a given year."""
    # OBIS-SEAMAP NARWSS yearly datasets follow pattern: https://seamap.env.duke.edu/dataset/10{year}
    url = f"https://seamap.env.duke.edu/api/dataset/10{year}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            print(f"\nOBIS-SEAMAP dataset 10{year}: HTTP 200 OK")
            data = resp.json()
            print(json.dumps(data, indent=2)[:2000])
        else:
            print(f"\nOBIS-SEAMAP dataset 10{year}: HTTP {resp.status_code}")
    except Exception as e:
        print(f"\nOBIS-SEAMAP dataset 10{year}: {e}")

def check_whalemap_api():
    """Check WhaleMap API for NARW sightings April 2017 in study region."""
    print("\n=== WhaleMap API ===")
    # WhaleMap REST API
    url = "https://whalemap.ocean.dal.ca/WhaleMap/api/right_whale"
    params = {
        "start": "2017-04-01",
        "end": "2017-04-30",
        "min_lat": 41.0,
        "max_lat": 43.5,
        "min_lon": -71.5,
        "max_lon": -68.5
    }
    try:
        resp = requests.get(url, params=params, timeout=15)
        print(f"  Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"  Records: {len(data) if isinstance(data, list) else data}")
            if isinstance(data, list) and data:
                print(f"  Sample keys: {list(data[0].keys())}")
        else:
            print(f"  Response: {resp.text[:500]}")
    except Exception as e:
        print(f"  Error: {e}")

def check_robots4whales():
    """Check Robots4Whales / WHOI buoy data availability."""
    print("\n=== Robots4Whales / WHOI Acoustic Buoy Data ===")
    # Acoustic Buoy Data API
    url = "https://robots4whales.whoi.edu/api/detections"
    params = {
        "start": "2017-04-01",
        "end": "2017-04-30",
        "species": "Eubalaena glacialis"
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        print(f"  Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"  Response snippet: {resp.text[:300]}")
        else:
            print(f"  Response: {resp.text[:200]}")
    except Exception as e:
        print(f"  Error (endpoint may require auth or be unavailable): {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("NOAA/OBIS Supplementary Audit - Part 2")
    print("=" * 60)
    
    # AMAPPS datasets that appeared in the first OBIS search
    amapps_spring_2012 = "ae75d50b-5b18-44f2-85ff-17879a7f3f5a"
    amapps_winter_2011 = "035be567-3064-485e-9773-b936f0482cbb"
    amapps_fall_2012   = "65bb59f2-99fb-4d13-a427-ae49a8dc13d5"
    amapps_winter_2014 = "45881aeb-30c9-4c19-9723-b0655b0609d5"
    amapps_spring_2014 = "0a3d1f18-2f69-4fae-bb1d-f2cca98c980a"
    
    print("\n=== AMAPPS Datasets - Study Region Coverage ===")
    for ds_id, label in [
        (amapps_spring_2012, "AMAPPS NE Aerial Spring 2012"),
        (amapps_winter_2011, "AMAPPS NE Aerial Winter 2011"),
        (amapps_fall_2012,   "AMAPPS NE Aerial Fall 2012"),
        (amapps_winter_2014, "AMAPPS NE Aerial Winter 2014"),
        (amapps_spring_2014, "AMAPPS NE Aerial Spring 2014"),
    ]:
        check_obis_dataset_records(ds_id, label)
    
    # Check OBIS-SEAMAP year-specific datasets
    print("\n=== OBIS-SEAMAP NARWSS Year Datasets ===")
    for yr in ["2017", "2016", "2018"]:
        check_obis_seamap_url(yr)
    
    # WhaleMap
    check_whalemap_api()
    
    # Robots4Whales
    check_robots4whales()
