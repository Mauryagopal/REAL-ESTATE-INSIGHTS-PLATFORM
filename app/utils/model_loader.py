import json
import joblib
import pandas as pd
from pathlib import Path

# Ensure pipeline deps import cleanly when loading joblib
import category_encoders as ce  # noqa: F401
from xgboost import XGBRegressor  # noqa: F401
from sklearn.ensemble import RandomForestRegressor  # noqa: F401

_MODEL = None
_EXPECTED_COLUMNS = None
_SCHEMA_EXAMPLES = None

def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]

def get_model():
    global _MODEL
    if _MODEL is None:
        model_path = _project_root() / "Saved_Model" / "gurgaon_price_model.joblib"
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found at {model_path}")
        _MODEL = joblib.load(model_path)
    return _MODEL

def get_expected_columns():
    global _EXPECTED_COLUMNS
    if _EXPECTED_COLUMNS is None:
        cols_path = _project_root() / "Saved_Model" / "expected_columns.json"
        if not cols_path.exists():
            raise FileNotFoundError(f"Columns file not found at {cols_path}")
        with open(cols_path, "r") as f:
            cols = json.load(f)
        _EXPECTED_COLUMNS = pd.Index(cols)
    return _EXPECTED_COLUMNS

def get_schema_examples():
    global _SCHEMA_EXAMPLES
    if _SCHEMA_EXAMPLES is None:
        examples_path = _project_root() / "Saved_Model" / "expected_columns_with_examples.json"
        if examples_path.exists():
            with open(examples_path, "r", encoding="utf-8") as f:
                _SCHEMA_EXAMPLES = json.load(f)
        else:
            _SCHEMA_EXAMPLES = {}
    return _SCHEMA_EXAMPLES

def get_allowed_values():
    # Pull choices from examples file; fallback to sensible defaults
    schema = get_schema_examples()
    cats = schema.get("categorical_values", {})

    fallback = {
        "property_type": ["Apartment", "House"],
        "balcony": ["yes", "no"],
        "agePossession": ["Ready to Move", "Under Construction", "0-1 Year Old Property", "1-5 Year Old Property", "5-10 Year Old Property", "New Launch"],
        "furnishing_type": ["unfurnished", "semifurnished", "furnished"],
        "luxury_category": ["budget", "mid", "luxury", "ultra"],
        "floor_category": ["ground", "low", "mid", "high"],
        "sector":["sector 36", "sector 89", "sohna road", "sector 92", "sector 102", 
            "gwal pahari", "sector 108", "sector 105", "sector 26", "sector 109",
            "sector 28", "sector 65", "sector 12", "sector 85", "sector 70a", 
            "sector 30", "sector 107", "sector 3", "sector 2", "sector 41", 
            "sector 4", "sector 62", "sector 49", "sector 81", "sector 66", 
            "sector 86", "sector 48", "sector 51", "sector 37", "sector 111", 
            "sector 67", "sector 113", "sector 13", "sector 61", "sector 69", 
            "sector 67a", "sector 37d", "sector 82", "sector 53", "sector 74", 
            "sector 52", "sector 43", "sector 14", "sector 25", "sector 95", 
            "sector 56", "sector 83", "sector 104", "sector 88a", "sector 55", 
            "sector 50", "sector 84", "sector 91", "sector 76", "sector 82a", 
            "sector 78", "manesar", "sector 93", "sector 7", "sector 71", 
            "sector 110", "sector 33", "sector 70", "sector 103", "sector 90", 
            "sector 38", "sector 79", "sector 112", "sector 22", "sector 59", 
            "sector 99", "sector 9", "sector 58", "sector 77", "sector 1", 
            "sector 57", "sector 106", "dwarka expressway", "sector 63", 
            "sector 5", "sector 40", "sector 23", "sector 6", "sector 72", 
            "sector 47", "sector 45", "sector 68", "sector 11", "sector 60", 
            "sector 39", "sector 63a", "sector 24", "sector 46", "sector 17", 
            "sector 15", "sector 10", "sector 31", "sector 21", "sector 80", 
            "sector 73", "sector 54", "sector 8", "sector 88", "sector 27"]# sector list can be large; pull from file if present
    }

    # Merge and sort while keeping uniqueness
    allowed = {}
    for k, default_vals in fallback.items():
        vals = cats.get(k, default_vals)
        # Ensure strings and strip spaces
        allowed[k] = sorted({str(v).strip() for v in vals})
    return allowed

def get_numeric_hints():
    schema = get_schema_examples()
    hints = schema.get("numeric_hints", {})
    fallback = {
        "bedRoom": {"min": 1, "max": 10, "step": 1},
        "bathroom": {"min": 1, "max": 10, "step": 1},
        "built_up_area": {"min": 100, "max": 10000, "step": 10},
        "servant_room": {"min": 0, "max": 5, "step": 1},
        "store_room": {"min": 0, "max": 5, "step": 1},
    }
    # Merge with fallback
    for k, v in fallback.items():
        if k not in hints:
            hints[k] = v
        else:
            hints[k] = {**v, **hints[k]}
    return hints