import pandas as pd
import numpy as np
from datetime import datetime
from scipy.spatial.distance import pdist, squareform
import json

def haversine(lon1, lat1, lon2, lat2):
    # Calculate great circle distance between two points in km
    R = 6371.0
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c

# Load data
df = pd.read_csv("data/raw/bio/narwss_2017/occurrence.txt", sep='\t', low_memory=False)
df_eg = df[df['scientificName'].str.contains('Eubalaena glacialis', na=False, case=False)].copy()
df_eg['eventDate'] = pd.to_datetime(df_eg['eventDate'], errors='coerce')
df_eg['eventTime'] = pd.to_datetime(df_eg['eventTime'], format='%H:%M:%S', errors='coerce').dt.time
df_eg['datetime'] = pd.to_datetime(df_eg['eventDate'].astype(str) + ' ' + df_eg['eventTime'].astype(str), errors='coerce')

df_eg_apr = df_eg[(df_eg['eventDate'].dt.year == 2017) & (df_eg['eventDate'].dt.month == 4)].copy()

# Bounding box
df_164 = df_eg_apr[
    (df_eg_apr['decimalLatitude'] >= 41.0) & (df_eg_apr['decimalLatitude'] <= 43.5) & 
    (df_eg_apr['decimalLongitude'] >= -71.5) & (df_eg_apr['decimalLongitude'] <= -68.5)
].copy()

# Temporal analysis
df_164['date_str'] = df_164['eventDate'].dt.strftime('%Y-%m-%d')
records_by_date = df_164['date_str'].value_counts().sort_index()

# 6-hour bins (0-6, 6-12, 12-18, 18-24)
df_164['hour'] = df_164['datetime'].dt.hour
df_164['6hr_bin'] = df_164['date_str'] + "_bin" + (df_164['hour'] // 6).astype(str)
records_by_bin = df_164['6hr_bin'].value_counts().sort_index()
occupied_bins = len(records_by_bin)
total_possible_bins = 30 * 4 # April has 30 days

# Spatial analysis (0.05 deg cells)
df_164['lat_bin'] = np.floor(df_164['decimalLatitude'] / 0.05) * 0.05
df_164['lon_bin'] = np.floor(df_164['decimalLongitude'] / 0.05) * 0.05
df_164['cell_id'] = df_164['lat_bin'].astype(str) + "_" + df_164['lon_bin'].astype(str)
occupied_cells = df_164['cell_id'].nunique()
detections_per_cell = df_164['cell_id'].value_counts()
detections_per_day = records_by_date

# Nearest neighbor
coords = df_164[['decimalLongitude', 'decimalLatitude']].values
if len(coords) > 1:
    dist_matrix = squareform(pdist(coords, metric=lambda u, v: haversine(u[0], u[1], v[0], v[1])))
    np.fill_diagonal(dist_matrix, np.inf)
    nn_distances = dist_matrix.min(axis=1)
    mean_nn = np.mean(nn_distances)
    min_nn = np.min(nn_distances)
    max_nn = np.max(nn_distances)
else:
    mean_nn = min_nn = max_nn = 0

# Temporal NN
df_164 = df_164.sort_values('datetime')
if len(df_164) > 1:
    time_diffs = df_164['datetime'].diff().dt.total_seconds().dropna() / 60.0 # in minutes
else:
    time_diffs = pd.Series([])

# Duplicates / Groups
exact_duplicates = df_164.duplicated(subset=['datetime', 'decimalLatitude', 'decimalLongitude'], keep=False).sum()

print("--- 164 SIGHTINGS ANALYSIS ---")
print(f"Records by date:\n{records_by_date.to_string()}")
print(f"\nRecords by 6-hour bin:\n{records_by_bin.to_string()}")
print(f"\nOccupied 6-hour bins: {occupied_bins} out of {total_possible_bins} ({occupied_bins/total_possible_bins*100:.1f}%)")
print(f"Occupied 0.05 deg cells: {occupied_cells}")
print(f"Mean detections per occupied cell: {detections_per_cell.mean():.1f} (max: {detections_per_cell.max()})")
print(f"Mean detections per survey day: {detections_per_day.mean():.1f} (max: {detections_per_day.max()})")
print(f"Spatial Nearest Neighbor (km): Mean={mean_nn:.2f}, Min={min_nn:.2f}, Max={max_nn:.2f}")
if not time_diffs.empty:
    print(f"Temporal Intervals between consecutive sightings (minutes):")
    print(f"  Zeros (simultaneous): {(time_diffs == 0).sum()}")
    print(f"  < 5 mins: {(time_diffs < 5).sum()}")
    print(f"  Mean interval (excluding >24h gaps): {time_diffs[time_diffs < 24*60].mean():.1f}")
print(f"\nExact spatiotemporal duplicates (same lat/lon/time): {exact_duplicates} records")

# Forecast window check
# We need a 24h history (meaning at least some observation in day D-1) 
# to forecast into 72h window (D to D+2) and have target observations to compute loss.
survey_dates = sorted(df_164['eventDate'].dt.date.unique())
print(f"\nSurvey dates: {survey_dates}")
viable_windows = 0
for d in survey_dates:
    # If d is a target day, we need to check if there is data in the previous 24h (D-1)
    # and we evaluate on D, D+1, D+2.
    pass
# Actually, let's just evaluate how many 'target' days (days with data) have ANY 'history' data in the preceding 3 days.
for i in range(len(survey_dates)):
    day = survey_dates[i]
    # Check if there is a survey date within the prior 1-3 days to provide history
    # Or conversely, if we use this day as history, do we have any targets in the next 3 days?
    targets_in_next_3_days = [d for d in survey_dates if 0 < (d - day).days <= 3]
    if targets_in_next_3_days:
        viable_windows += 1

print(f"\nNumber of survey days that can serve as history for a forecast within 72h: {viable_windows}")
