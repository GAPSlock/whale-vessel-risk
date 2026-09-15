import requests
import zipfile
import io
import pandas as pd
import os

url = "https://ipt.env.duke.edu/archive.do?r=zd_102017"

out_dir = "data/raw/bio/narwss_2017"
os.makedirs(out_dir, exist_ok=True)

print(f"Downloading {url} ...")
res = requests.get(url, timeout=30)
res.raise_for_status()

with zipfile.ZipFile(io.BytesIO(res.content)) as z:
    z.extractall(out_dir)

print(f"Extracted to {out_dir}:")
for f in os.listdir(out_dir):
    fpath = os.path.join(out_dir, f)
    size = os.path.getsize(fpath)
    print(f"- {f} ({size} bytes)")
    
    if f.endswith('.txt') or f.endswith('.csv'):
        # Usually tab-separated in DwC-A
        sep = '\t'
        try:
            df = pd.read_csv(fpath, sep=sep, low_memory=False)
            print(f"  Rows: {len(df)}")
            print(f"  Cols: {list(df.columns)}")
        except Exception as e:
            print(f"  Error reading {f}: {e}")

