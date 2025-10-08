import joblib
import pandas as pd
import json
from pathlib import Path

MODEL_PATH = Path("Saved_Model/gurgaon_price_model.joblib")
COLUMNS_PATH = Path("Saved_Model/expected_columns.json")

model = joblib.load(MODEL_PATH)
expected_columns = pd.Index(json.load(open(COLUMNS_PATH)))

def predict_price(payload: dict):
    X_new = pd.DataFrame([payload])
    X_new = X_new.reindex(columns=expected_columns)
    prediction = model.predict(X_new)[0]
    return round(float(prediction), 2)
