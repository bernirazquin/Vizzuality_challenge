from pathlib import Path
import requests, zipfile
import geopandas as gpd
import pandas as pd
import numpy as np
import rasterio
from rasterio.mask import mask
from rasterstats import zonal_stats
from rasterio.plot import show
from rasterio.enums import Resampling
import matplotlib.pyplot as plt
import warnings
import sqlite3


# Base directories.
BASE_DIR = Path.cwd()
DATA_DIR = BASE_DIR / "data"
RAW = DATA_DIR / "raw"
PROCESSED = DATA_DIR / "processed"
OUTPUT = DATA_DIR / "output"

for folder in [RAW, PROCESSED, OUTPUT]:
    folder.mkdir(parents=True, exist_ok=True)

print("Folders are ready:", list(DATA_DIR.glob('*')))


# ------------------------
#     DATA DOWNLOAD
# ------------------------
# 
# You can also execute .py file directly if wanted.


from download import download_and_extract, COUNTIES_URL, CARBON_URL

# Downloads
counties_dir = download_and_extract(COUNTIES_URL, RAW)
carbon_dir = download_and_extract(CARBON_URL, RAW)

# Find paths after download
shp_path = list(counties_dir.rglob("*.shp"))[0]
raster_path = next(carbon_dir.rglob("*.tif"))
print("Download completed.")


# ------------------------
#     COUNTY FILTERING
# ------------------------


gdf = gpd.read_file(shp_path)

filtered = gdf[gdf["STATEFP"].isin(["26", "27", "55"])].copy() # Michigan (26), Minnesota (27), Wisconsin (55). 
filtered_path = PROCESSED / "counties_MI_WI_MN.gpkg" # Change to gpkg for file consistency
filtered.to_file(filtered_path, driver="GPKG")

print(f"Geopackage saved in: {filtered_path}")
print("County count", len(filtered))

# Obtains CRS from .gpkg, equals it to raster file and defines route to be used by Zonal Stats. 

print("\nRaster & counties correction")
print("Original raster path:", raster_path)

with rasterio.open(raster_path) as src:
    raster_crs = src.crs
    
    # 1. Reproyects de .gpkg file to equal rasters CRS. 
    gdf_reproj = gpd.read_file(filtered_path).to_crs(raster_crs)
    
    # 2. Saves the reproyected .pgpk for future use
    filtered_path_reproj = PROCESSED / "counties_reproj.gpkg"
    gdf_reproj.to_file(filtered_path_reproj, driver="GPKG")
    
    clipped_raster = raster_path # Due to RAM limitations...  

print(f"New Geopackage saved in: {filtered_path_reproj}")


# ------------------------
#     UNITS CONVERSION
# ------------------------


print("\nCalculating total carbon per county...")

# Converts Units in original raster Mg CO₂e/acre to Mg C/pixel. Needed to Sum Total Carbon per county. 

# FACTOR = (Mg CO₂e/acre to Mg C/pixel)
FACTOR = (900 / 4046.86) * (12 / 44) 
NODATA_ORIGINAL = 65535 # Raster's Nodata value
MAX_VALUE = 173 # Maximum clipping value used in the original analysis. Just a error check point.

def sum_cleaned_raw(a):
    """Sum raw pixels (Mg CO₂e/acre) after NoData cleaning and clipping."""
    
    # FIX: Convert to float32 to allow np.nan and do float calculations
    a = a.astype(np.float32) 
    
    # 1. Cleaning
    a[a == NODATA_ORIGINAL] = np.nan # Apply NoData
    a[a > MAX_VALUE] = np.nan        # Removes inflated values if they exist. 
    
    # 2. Total sum of clean raw values
    return np.nansum(a)

def count_valid_pixels(a):
    """Count the number of valid pixels after cleaning."""
    # Just another checkpoint, had some trouble "Relying" on output values. 
    a = a.astype(np.float32) 
    a[a == NODATA_ORIGINAL] = np.nan
    a[a > MAX_VALUE] = np.nan
    return np.nansum(np.isfinite(a))


# Reads reprojected polygons
gdf = gpd.read_file(filtered_path_reproj) 



# ------------------------
#     ZONAL STATS
# ------------------------



print(" Converting units and running zonal stats...")

'''Temporarily suppress rasterstats warnings due to nodata in custom stats. had some
    issues with noData values, found this way to prevent it from processing data'''

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    stats = zonal_stats(
        vectors=gdf,
        raster=str(clipped_raster), # Use path to ORIGINAL raster
        stats=[], 
        add_stats={'raw_sum_CO2e_acre': sum_cleaned_raw, 'valid_pixels': count_valid_pixels},
        geojson_out=False,
        nodata=NODATA_ORIGINAL, 
        all_touched=False
    )

# Add columns
gdf["raw_sum_CO2e_acre"] = [s["raw_sum_CO2e_acre"] for s in stats]
gdf["valid_pixels"] = [s["valid_pixels"] for s in stats]

# Conversion of units to Mg C
print("Applying conversion factor (Mg CO₂e/acre to Mg C)...")
gdf["total_MgC"] = gdf["raw_sum_CO2e_acre"] * FACTOR

# Removes columns we don't use/want
columns_to_drop = [
    "COUNTYNS", "GEOIDFQ", "LSAD", "MTFCC", "CSAFP","CBSAFP","CLASSFP", 
    "METDIVFP", "FUNCSTAT", "ALAND", "AWATER", "INTPTLAT", "INTPTLON"
]

# Only drop columns that actually exist (one more check-point for errors)
gdf = gdf.drop(columns=[c for c in columns_to_drop if c in gdf.columns])

print(f"Dropped columns: {[c for c in columns_to_drop if c not in gdf.columns]}")

# Export results
out_gpkg = OUTPUT / "carbon_total_by_county.gpkg"
gdf.to_file(out_gpkg, driver="GPKG")

print(f"\nGeoPackage saved in: {out_gpkg}")
print("\nPreview of results:")
print(gdf[["NAME", "raw_sum_CO2e_acre", "valid_pixels", "total_MgC"]].head())
print(f"\n Process completed successfully. Total counties processed: {len(gdf)}")

db_path = "data/output/total_carbon.db"


# --------------------------
#       DATA BASE UPLOAD
# --------------------------
 

# Connect to SQLite
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Shows the tables containd in the db. 
print("Tables in database:")
tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
for t in tables:
    print(" -", t[0])

# grabs the column info for the main table
print("\nTable structure for 'total_carbon':")
columns = cursor.execute("PRAGMA table_info(total_carbon);").fetchall()
for col in columns:
    print(f" - {col[1]} ({col[2]})")

# Previews the first few rows
print("\n Data preview:")
df_preview = pd.read_sql("SELECT * FROM total_carbon LIMIT 5;", conn)
print(df_preview)

conn.close()

print(f"""
Pipeline completed successfully.
For previsualizations, output visualizations and database queries,
check total_carbon_pipeline.ipynb.
""")
