"""Loads editable NGO data from JSON so content updates without code changes."""
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_json(name, default=None):
    path = DATA_DIR / name
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError):
        return default if default is not None else {}


def ngo():
    return load_json("ngo.json", {})
