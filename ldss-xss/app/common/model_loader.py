import os
import re
import nltk
from sentence_transformers import SentenceTransformer
from django.conf import settings
from .symlink_check import symlink_check

import logging as logger

_initialized = False
_semantic_model = None

def reassemble_chunked_files(directory: str, allowed_base: str) -> None:
    symlink_check(directory, allowed_base)
    part_regex = re.compile(r"^(.*)\.part(\d+)$")
    parts_dict = {}
    for fname in os.listdir(directory):
        full_path = os.path.join(directory, fname)
        symlink_check(full_path, allowed_base)
        match = part_regex.match(fname)
        if match:
            base, num = match.group(1), int(match.group(2))
            parts_dict.setdefault(base, []).append((num, fname))
    for base, parts in parts_dict.items():
        parts.sort()
        output_path = os.path.join(directory, base)
        symlink_check(output_path, allowed_base)
        with open(output_path, "wb") as out:
            for _, part in parts:
                part_path = os.path.join(directory, part)
                symlink_check(part_path, allowed_base)
                with open(part_path, "rb") as pf:
                    out.write(pf.read())
                os.remove(part_path)

def initialize_models():
    global _initialized, _semantic_model
    if _initialized:
        return

    root_dir    = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    models_root = os.path.join(root_dir, "models")
    allowed_base = root_dir

    symlink_check(models_root, allowed_base)
    os.makedirs(models_root, exist_ok=True)

    nltk_data_dir = os.path.join(models_root, "nltk_data")
    symlink_check(nltk_data_dir, allowed_base)
    os.makedirs(nltk_data_dir, exist_ok=True)
    nltk.data.path.append(nltk_data_dir)

    model_dir = os.path.join(models_root, "all-mpnet-base-v2")
    symlink_check(model_dir, allowed_base)
    os.makedirs(model_dir, exist_ok=True)

    if any(fname.endswith(f".part{n}") for fname in os.listdir(model_dir) for n in range(1, 1000)):
        reassemble_chunked_files(model_dir, allowed_base)

    config_path = os.path.join(model_dir, "config.json")
    symlink_check(config_path, allowed_base)
    if os.path.isfile(config_path):
        load_dir = model_dir
    else:
        raise FileNotFoundError("…")

    _semantic_model = SentenceTransformer(load_dir)
    _initialized = True

def get_semantic_model() -> SentenceTransformer:
    if not _initialized:
        initialize_models()
    return _semantic_model
