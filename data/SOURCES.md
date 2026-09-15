# Data Sources

| # | Dataset | Purpose | Source | Access method | Format | License note |
|---|---|---|---|---|---|---|
| 1 | Historical AIS vessel traffic (U.S. waters) | Vessel positions, speed, heading, MMSI | [NOAA Marine Cadastre](https://marinecadastre.gov/ais/) | Bulk ZIP download | CSV | Public domain (U.S. government) |
| 2 | Right whale acoustic detections | Ground-truth presence signal | [WHOI Robots4Whales](http://dcs.whoi.edu/) & [NOAA NEFSC](https://www.fisheries.noaa.gov/new-england-mid-atlantic/science-data/passive-acoustic-research-northeast) | Manual/API | CSV | Check dataset terms |
| 3 | Right whale visual sightings | Additional ground-truth presence points | [WhaleMap](https://whalemap.org/) & [OBIS-SEAMAP](https://seamap.env.duke.edu/) | API export | CSV/JSON | Public, cite per dataset |
| 4 | Ocean surface currents | Physics prior for Module A, PDE forcing term | [Copernicus Marine Service](https://marine.copernicus.eu/) (GLORYS12V1) | `copernicusmarine` Python client | NetCDF | Free with registration; credit Copernicus |
| 5 | Wind fields | Secondary forcing term | [ECMWF ERA5 via Copernicus CDS](https://cds.climate.copernicus.eu/) | `cdsapi` Python client | NetCDF | Free with registration; credit ECMWF/C3S |
| 6 | Bathymetry | Static feature (depth-driven habitat preference) | [GEBCO](https://www.gebco.net/) | Direct download | NetCDF | Free, public |
| 7 | Chlorophyll-a | Prey-density proxy (optional v1 enrichment) | [NASA Ocean Color ERDDAP](https://coastwatch.pfeg.noaa.gov/erddap/) | ERDDAP API | NetCDF | Public |
| 8 | Historical ship-strike incident records | Validation ground truth | NOAA National Stranding/Mortality database | Public reports | PDF/CSV | Public |
| 9 | NOAA Seasonal Management Areas | Baseline-1 comparison system | [NOAA Right Whale Speed Rule](https://www.fisheries.noaa.gov/national/endangered-species-conservation/reducing-vessel-strikes-north-atlantic-right-whales) | Direct shapefile download | Shapefile | Public |
| 10 | Shipping lanes / TSS | Constrains realistic routing search space | [NOAA Office of Coast Survey](https://nauticalcharts.noaa.gov/data/gis-data-and-services.html) | Direct download | S-57/Shapefile | Public |

*All URLs verified successfully.*
