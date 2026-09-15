import pandas as pd

df = pd.read_csv("data/raw/bio/narwss_2017/occurrence.txt", sep='\t', low_memory=False)
total_records = len(df)

# Filter Eubalaena glacialis
df_eg = df[df['scientificName'].str.contains('Eubalaena glacialis', na=False, case=False)].copy()

print(f"Total records in archive: {total_records}")
print(f"Total E. glacialis records: {len(df_eg)}")

df_eg['eventDate'] = pd.to_datetime(df_eg['eventDate'], errors='coerce')
df_eg['month'] = df_eg['eventDate'].dt.month
df_eg['year'] = df_eg['eventDate'].dt.year

df_eg_apr = df_eg[(df_eg['year'] == 2017) & (df_eg['month'] == 4)].copy()
print(f"E. glacialis in April 2017: {len(df_eg_apr)}")

# Bounding box: 41.0 to 43.5 N, -71.5 to -68.5 W
df_eg_apr_bb = df_eg_apr[
    (df_eg_apr['decimalLatitude'] >= 41.0) & 
    (df_eg_apr['decimalLatitude'] <= 43.5) & 
    (df_eg_apr['decimalLongitude'] >= -71.5) & 
    (df_eg_apr['decimalLongitude'] <= -68.5)
].copy()

print(f"E. glacialis in April 2017 AND bounding box: {len(df_eg_apr_bb)}")

print(f"Unique dates (April/bbox): {df_eg_apr_bb['eventDate'].dt.date.nunique()}")
if 'eventID' in df_eg_apr_bb.columns:
    print(f"Unique event IDs: {df_eg_apr_bb['eventID'].nunique()}")
else:
    print(f"Unique event IDs: Not present (no eventID column)")

print(f"Unique individuals: Not present (no individual tracking ID column)")

print("Spatial extent (April/bbox):")
print(f"  Lat: {df_eg_apr_bb['decimalLatitude'].min():.4f} to {df_eg_apr_bb['decimalLatitude'].max():.4f}")
print(f"  Lon: {df_eg_apr_bb['decimalLongitude'].min():.4f} to {df_eg_apr_bb['decimalLongitude'].max():.4f}")

# What's in dynamicProperties?
if 'dynamicProperties' in df_eg_apr_bb.columns:
    print("Sample dynamicProperties:")
    print(df_eg_apr_bb['dynamicProperties'].head(3).tolist())
