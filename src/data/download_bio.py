import os
import requests
import pandas as pd
import json

def fetch_obis_data(start_date, end_date, output_csv):
    """
    Fetches Eubalaena glacialis (NARW) occurrences from OBIS API.
    Separates into acoustic and visual based on basisOfRecord.
    """
    print(f"Fetching OBIS data from {start_date} to {end_date}...")
    
    url = "https://api.obis.org/v3/occurrence"
    
    # Eubalaena glacialis taxon ID: 137094
    # Bounding box: Gulf of Maine & Cape Cod Bay (41.0 to 43.5 N, -71.5 to -68.5 W)
    # OBIS API geometry parameter requires WKT string.
    # WKT POLYGON coordinates must be longitude, latitude
    wkt_polygon = "POLYGON((-71.5 41.0, -68.5 41.0, -68.5 43.5, -71.5 43.5, -71.5 41.0))"
    
    params = {
        "taxonid": 137094,
        "geometry": wkt_polygon,
        "startdate": start_date,
        "enddate": end_date,
        "size": 5000  # max per page
    }
    
    all_records = []
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if 'results' in data:
            all_records.extend(data['results'])
            
        print(f"Total records fetched: {len(all_records)}")
        
        if len(all_records) > 0:
            df = pd.DataFrame(all_records)
            
            # Select key columns
            cols = ['id', 'decimalLatitude', 'decimalLongitude', 'eventDate', 
                    'basisOfRecord', 'datasetName', 'individualCount']
            
            # Keep only columns that exist
            cols = [c for c in cols if c in df.columns]
            df = df[cols]
            
            df.to_csv(output_csv, index=False)
            print(f"Saved to {output_csv}")
            
            # Basic stats
            if 'basisOfRecord' in df.columns:
                print("Counts by basisOfRecord:")
                print(df['basisOfRecord'].value_counts())
            return df
        else:
            print("No records found for this temporal/spatial query.")
            return None
            
    except Exception as e:
        print(f"Error fetching OBIS data: {e}")
        return None

if __name__ == "__main__":
    os.makedirs("data/raw/bio", exist_ok=True)
    fetch_obis_data("2017-04-01", "2017-04-30", "data/raw/bio/obis_narw_2017_04.csv")
