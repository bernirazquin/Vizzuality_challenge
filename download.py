from pathlib import Path
import requests, zipfile

# === URLs to download ===
COUNTIES_URL = "https://www2.census.gov/geo/tiger/TIGER2025/COUNTY/tl_2025_us_county.zip"
CARBON_URL = "https://usfs-public.box.com/shared/static/v861gwms9fq68sitl0r3vs2v3moxeu9x.zip"


def download_and_extract(url, output_dir):
    """Download and extract a ZIP file only if not already present and extracted."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    zip_path = output_dir / Path(url).name
    extract_dir = output_dir / Path(url).stem

# Skips if folders already exist.
    if zip_path.exists() and extract_dir.exists() and any(extract_dir.iterdir()):
        print(f"Skipping: {extract_dir.name} already exists.")
        return extract_dir

# If ZIP doesn't exist, download it.
    if not zip_path.exists():
        print(f"Downloading {url}")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(zip_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("Download complete.")
    else:
        print(f"ZIP already downloaded: {zip_path.name}")

# Extract when necessary.
    if not extract_dir.exists() or not any(extract_dir.iterdir()):
        print(f"📂 Extracting to {extract_dir.name}...")
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(extract_dir)
        print("Extraction complete.")
    else:
        print(f"Files already extracted: {extract_dir.name}")

    return extract_dir

## Run the download.py file directly ##

if __name__ == "__main__":
    # === Download configuration ===
    RAW = Path("data/raw")
    RAW.mkdir(parents=True, exist_ok=True)

    # Downloads
    counties_dir = download_and_extract(COUNTIES_URL, RAW)
    carbon_dir = download_and_extract(CARBON_URL, RAW)

    # Search for important files
    shp_path = list(counties_dir.rglob("*.shp"))[0]
    raster_path = next(carbon_dir.rglob("*.tif"))

    print("✅ Download completed.")
    print(f"Shapefile path: {shp_path}")
    print(f"Raster path: {raster_path}")

