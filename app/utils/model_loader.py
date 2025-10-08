import json
import joblib
import pandas as pd
from pathlib import Path

# Important: ensure dependencies used in the saved pipeline are importable
import category_encoders as ce  # noqa: F401
from xgboost import XGBRegressor  # noqa: F401
from sklearn.ensemble import RandomForestRegressor  # noqa: F401

_MODEL = None
_EXPECTED_COLUMNS = None

def _project_root() -> Path:
    # app/utils/model_loader.py -> up two dirs -> project root
    return Path(__file__).resolve().parents[2]

def lazy_load():
    global _MODEL, _EXPECTED_COLUMNS
    if _MODEL is not None and _EXPECTED_COLUMNS is not None:
        return

    model_path = _project_root() / "Saved_Model" / "gurgaon_price_model.joblib"
    cols_path = _project_root() / "Saved_Model" / "expected_columns.json"

    if not model_path.exists():
        raise FileNotFoundError(f"Model not found at {model_path}")
    if not cols_path.exists():
        raise FileNotFoundError(f"Columns file not found at {cols_path}")

    _MODEL = joblib.load(model_path)
    with open(cols_path, "r") as f:
        cols = json.load(f)
    _EXPECTED_COLUMNS = pd.Index(cols)

def get_model():
    lazy_load()
    return _MODEL

def get_expected_columns():
    lazy_load()
    return _EXPECTED_COLUMNS