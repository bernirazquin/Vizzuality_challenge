from pathlib import Path
import requests, zipfile

def download_and_extract(url, output_dir):
    """Download and extract a ZIP file only if not already present and extracted."""
    output_dir.mkdir(parents=True, exist_ok=True)
    zip_path = output_dir / Path(url).name
    extract_dir = output_dir / Path(url).stem

    # Skips if folders already exists. 
    if zip_path.exists() and extract_dir.exists() and any(extract_dir.iterdir()):
        print(f"Skipping: {extract_dir.name} already exists with content.")
        return extract_dir

    # Si falta el ZIP, descarga
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

    # 📂 Si falta la carpeta extraída o está vacía, extrae
    if not extract_dir.exists() or not any(extract_dir.iterdir()):
        print(f"📂 Extracting to {extract_dir.name}...")
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(extract_dir)
        print("Extraction complete.")
    else:
        print(f"Files already extracted: {extract_dir.name}")

    return extract_dir

