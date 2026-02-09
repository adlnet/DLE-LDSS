import nltk
from pathlib import Path
import shutil
import sys

DATA_DIR = Path(__file__).parent.parent.parent / "app" / "models" / "nltk_data"
PACKAGES = ("punkt", "wordnet", "omw-1.4", "punkt_tab")

def download_packages(target_dir: Path):
    for pkg in PACKAGES:
        print(f"Downloading {pkg} into {target_dir}…")
        nltk.download(pkg, download_dir=str(target_dir))

def extract_archives(target_dir: Path):
    for zip_path in target_dir.rglob("*.zip"):
        shutil.unpack_archive(str(zip_path), extract_dir=str(zip_path.parent))
        zip_path.unlink()

def main():
    if DATA_DIR.exists():
        for item in DATA_DIR.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
    else:
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    try:
        download_packages(DATA_DIR)
        extract_archives(DATA_DIR)
    except Exception:
        sys.exit(1)

if __name__ == "__main__":
    main()
