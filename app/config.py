import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT_DIR, ".."))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")

    # Dataset paths (override via env if you want)
    DATASET_DIR = os.getenv("DATASET_DIR", os.path.join(PROJECT_ROOT, "Dataset"))
    IMPUTED_PATH = os.getenv("IMPUTED_PATH", os.path.join(DATASET_DIR, "gurgaon_properties_missing_value_imputation.csv"))
    PROPERTIES_PATH = os.getenv("PROPERTIES_PATH", os.path.join(DATASET_DIR, "gurgaon_properties.csv"))
    LATLONG_PATH = os.getenv("LATLONG_PATH", os.path.join(DATASET_DIR, "latlong.csv"))
    FEATURE_TEXT_PKL = os.getenv("FEATURE_TEXT_PKL", os.path.join(PROJECT_ROOT, "Saved_Model", "feature_text.pkl"))

    # Plotly CDN version (used in base.html)
    PLOTLY_CDN_VERSION = os.getenv("PLOTLY_CDN_VERSION", "2.32.0")