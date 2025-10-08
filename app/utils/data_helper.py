import json
import pandas as pd
from flask import current_app
from .model_loader import get_expected_columns

# UI fields -> dataset column names
# Note: dataset uses "servant room"/"store room" with spaces, so we map UI -> dataset
ALLOWED_FIELDS = [
    "bedRoom", "bathroom", "built_up_area", "servant_room", "store_room",
    "property_type", "sector", "balcony", "agePossession",
    "furnishing_type", "luxury_category", "floor_category"
]

NUMERIC_FIELDS = ["bedRoom", "bathroom", "built_up_area", "servant_room", "store_room"]
TEXT_FIELDS = [
    "property_type", "sector", "balcony", "agePossession",
    "furnishing_type", "luxury_category", "floor_category"
]

def ensure_schema_compatibility():
    expected = get_expected_columns()
    required = {"bedRoom","bathroom","built_up_area","servant room","store room",
                "property_type","sector","balcony","agePossession","furnishing_type",
                "luxury_category","floor_category"}
    missing = sorted(list(required - set(expected)))
    if missing:
        raise RuntimeError(f"Model is missing required columns: {missing}. "
                           "Share expected_columns.json so we can update the form/schema.")

def _coerce_numeric(val, default=0):
    if val is None or str(val).strip() == "":
        return default
    try:
        s = str(val).strip()
        return float(s) if "." in s else int(s)
    except Exception:
        return default

def form_to_dataframe(form_data: dict) -> pd.DataFrame:
    # Take only allowed fields
    clean = {k: form_data.get(k, "") for k in ALLOWED_FIELDS}

    # Coerce numerics
    for k in NUMERIC_FIELDS:
        clean[k] = _coerce_numeric(clean.get(k))

    # Normalize text
    for k in TEXT_FIELDS:
        clean[k] = str(clean.get(k, "")).strip()

    # Map UI keys to dataset column names with spaces
    clean["servant room"] = clean.pop("servant_room")
    clean["store room"] = clean.pop("store_room")

    df = pd.DataFrame([clean])
    expected_cols = get_expected_columns()
    # Only keep columns that model expects, and add any missing (as NaN)
    df = df.reindex(columns=expected_cols)
    return df

def convert_crore_to_inr(value_in_crore: float) -> float:
    return float(value_in_crore) * 1e7

def format_price(amount_in_inr: float) -> dict:
    # Pretty display + breakdown
    if amount_in_inr >= 1e7:
        main = f"₹{amount_in_inr / 1e7:.2f} Cr"
    elif amount_in_inr >= 1e5:
        main = f"₹{amount_in_inr / 1e5:.2f} Lakh"
    else:
        main = f"₹{amount_in_inr:,.0f}"

    return {
        "main": main,
        "inr": f"₹{amount_in_inr:,.0f}",
        "lakh": f"{amount_in_inr / 1e5:.2f} Lakh",
        "crore": f"{amount_in_inr / 1e7:.2f} Cr",
    }