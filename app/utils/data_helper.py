import pandas as pd
from typing import Tuple, Dict, Any, List

from .model_loader import get_expected_columns, get_allowed_values, get_numeric_hints

# UI fields (strict) — matches your model schema
ALLOWED_FIELDS = [
    "bedRoom", "bathroom", "built_up_area", "servant_room", "store_room",
    "property_type", "sector", "balcony", "agePossession",
    "furnishing_type", "luxury_category", "floor_category"
]

NUMERIC_FIELDS = ["bedRoom", "bathroom", "built_up_area", "servant_room", "store_room"]
CATEGORICAL_FIELDS = [
    "property_type", "sector", "balcony", "agePossession",
    "furnishing_type", "luxury_category", "floor_category"
]

def ensure_schema_compatibility() -> None:
    expected = set(get_expected_columns())
    required = {"bedRoom","bathroom","built_up_area","servant room","store room",
                "property_type","sector","balcony","agePossession",
                "furnishing_type","luxury_category","floor_category"}
    missing = sorted(list(required - expected))
    if missing:
        raise RuntimeError(f"Model is missing required columns: {missing}. "
                           "Adjust the form or update expected_columns.json.")

def _coerce_numeric(val, default=0):
    if val is None or str(val).strip() == "":
        return default
    try:
        s = str(val).strip()
        return float(s) if "." in s else int(s)
    except Exception:
        return default

def validate_and_prepare(form_data: Dict[str, Any]) -> Tuple[pd.DataFrame, List[str], Dict[str, Any]]:
    allowed = get_allowed_values()
    hints = get_numeric_hints()
    errors: List[str] = []

    # Keep only allowed fields
    clean: Dict[str, Any] = {k: form_data.get(k, "") for k in ALLOWED_FIELDS}

    # Validate numerics
    for f in NUMERIC_FIELDS:
        v = _coerce_numeric(clean.get(f))
        lim = hints.get(f, {})
        vmin, vmax = lim.get("min", None), lim.get("max", None)
        if vmin is not None and v < vmin:
            errors.append(f"{f} must be >= {vmin}")
        if vmax is not None and v > vmax:
            errors.append(f"{f} must be <= {vmax}")
        clean[f] = v

    # Validate categoricals
    for f in CATEGORICAL_FIELDS:
        val = str(clean.get(f, "")).strip()
        choices = allowed.get(f, [])
        if choices and val not in choices:
            errors.append(f"{f} must be one of: {', '.join(choices[:8])}{'...' if len(choices)>8 else ''}")
        clean[f] = val

    # Map to training schema (spaces)
    clean["servant room"] = clean.pop("servant_room")
    clean["store room"] = clean.pop("store_room")

    # Build dataframe in model’s expected order
    df = pd.DataFrame([clean]).reindex(columns=get_expected_columns())
    return df, errors, clean

def convert_crore_to_inr(value_in_crore: float) -> float:
    return float(value_in_crore) * 1e7

def format_price(amount_in_inr: float) -> Dict[str, str]:
    # Compact main + breakdown
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