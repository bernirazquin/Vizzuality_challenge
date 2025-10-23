
from pathlib import Path
import requests
import zipfile

# Where raw data will be stored
RAW = Path("data/raw")
RAW.mkdir(parents=True, exist_ok=True)

def download_and_extract(url, output_dir):
    # Path to save the ZIP file
    zip_path = output_dir / Path(url).name

    # Download if it doesn’t already exist
    if not zip_path.exists():
        print(f"⬇Downloading {url}")
        response = requests.get(url)
        response.raise_for_status()  # Raises an error if the download fails
        with open(zip_path, "wb") as f:
            f.write(response.content)
        print(f"File saved at {zip_path}")
    else:
        print(f"{zip_path.name} already exists. Skipping download...")

    # Extract ZIP if it hasn’t been extracted yet
    extract_dir = output_dir / Path(url).stem
    if not extract_dir.exists():
        print(f"📂 Extracting to {extract_dir}...")
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(extract_dir)
        print(f"Extraction complete: {extract_dir}")
    else:
        print(f"Folder {extract_dir.name} already exists. Skipping extraction...")

    return extract_dir


# Raster and counties shapefiles url's
COUNTIES_URL = "https://www2.census.gov/geo/tiger/TIGER2025/COUNTY/tl_2025_us_county.zip"
CARBON_URL = "https://usfs-public.box.com/shared/static/v861gwms9fq68sitl0r3vs2v3moxeu9x.zip"

# Run the downloads
if __name__ == "__main__":
    print("Starting downloads...\n")
    counties_dir = download_and_extract(COUNTIES_URL, RAW)
    carbon_dir = download_and_extract(CARBON_URL, RAW)
    print("\n All downloads completed successfully.")
