import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

def generate_mock_bio_data():
    """
    Generates synthetic biological data for software integration testing only.
    
    WARNING: THIS DATA IS SYNTHETIC. 
    It is explicitly tagged with 'SYNTHETIC_SOFTWARE_FIXTURE' and must NEVER 
    be used for scientific training, KDE validation, effort coverage, or ecological realism.
    """
    np.random.seed(42)
    start_date = datetime(2017, 4, 1)
    end_date = datetime(2017, 4, 30, 23, 59, 59)
    
    buoys = [
        {"lat": 41.9, "lon": -70.3, "name": "CCB_Buoy_1"},
        {"lat": 42.1, "lon": -70.4, "name": "CCB_Buoy_2"},
        {"lat": 42.3, "lon": -70.2, "name": "Stellwagen_Buoy_1"}
    ]
    
    acoustic_records = []
    for _ in range(1500):
        b = np.random.choice(buoys)
        dt = start_date + timedelta(seconds=np.random.randint(0, int((end_date - start_date).total_seconds())))
        
        acoustic_records.append({
            "timestamp": dt,
            "lat": b['lat'] + np.random.normal(0, 0.01),
            "lon": b['lon'] + np.random.normal(0, 0.01),
            "modality": "acoustic",
            "platform": b['name'],
            "count": 1,
            "DATA_SOURCE_FLAG": "SYNTHETIC_SOFTWARE_FIXTURE"
        })
        
    visual_records = []
    for _ in range(500):
        dt = start_date + timedelta(seconds=np.random.randint(0, int((end_date - start_date).total_seconds())))
        dt = dt.replace(hour=np.random.randint(10, 16))
        
        visual_records.append({
            "timestamp": dt,
            "lat": np.random.uniform(41.7, 42.5),
            "lon": np.random.uniform(-70.7, -69.8),
            "modality": "visual",
            "platform": "aerial_survey",
            "count": np.random.randint(1, 4),
            "DATA_SOURCE_FLAG": "SYNTHETIC_SOFTWARE_FIXTURE"
        })
        
    df = pd.DataFrame(acoustic_records + visual_records)
    df = df.sort_values("timestamp").reset_index(drop=True)
    
    os.makedirs("data/raw/bio", exist_ok=True)
    df.to_csv("data/raw/bio/mock_narw_2017_04.csv", index=False)
    return df

def generate_mock_visual_effort():
    np.random.seed(42)
    start_date = datetime(2017, 4, 1)
    
    tracks = []
    for i in range(10):
        dt = start_date + timedelta(days=np.random.randint(0, 30))
        dt = dt.replace(hour=10)
        lat, lon = 41.8, -70.5
        for step in range(50):
            lat += 0.01
            lon += np.random.choice([-0.05, 0.05])
            tracks.append({
                "flight_id": f"flight_{i}",
                "timestamp": dt + timedelta(minutes=step*2),
                "lat": lat,
                "lon": lon,
                "DATA_SOURCE_FLAG": "SYNTHETIC_SOFTWARE_FIXTURE"
            })
            
    df = pd.DataFrame(tracks)
    df.to_csv("data/raw/bio/mock_visual_effort_2017_04.csv", index=False)

if __name__ == "__main__":
    generate_mock_bio_data()
    generate_mock_visual_effort()
