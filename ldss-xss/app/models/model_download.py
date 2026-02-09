import os
import shutil
from sentence_transformers import SentenceTransformer
import sys

CHUNK_SIZE = 250 * 1024**2
HERE = os.path.dirname(os.path.abspath(__file__))
SAVE_DIR = os.path.join(HERE, "all-mpnet-base-v2")

def split_file(filepath, chunk_size=CHUNK_SIZE):
    file_size = os.path.getsize(filepath)
    if file_size <= chunk_size:
        return []
    part_files = []
    with open(filepath, "rb") as f:
        part_num = 1
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            part_filename = f"{filepath}.part{part_num}"
            with open(part_filename, "wb") as pf:
                pf.write(chunk)
            part_files.append(part_filename)
            part_num += 1
    os.remove(filepath)
    return part_files

def process_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            filepath = os.path.join(root, file)
            size = os.path.getsize(filepath)
            if size > CHUNK_SIZE:
                split_file(filepath)

def main():
    if os.path.isdir(SAVE_DIR):
        shutil.rmtree(SAVE_DIR)
    try:
        model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
        model.save(SAVE_DIR)
        process_directory(SAVE_DIR)
    except Exception:
        sys.exit(1)

if __name__ == "__main__":
    main()
