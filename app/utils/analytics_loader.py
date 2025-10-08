# app/utils/analytics_loader.py
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Optional, List

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio

# Optional wordcloud
try:
    from wordcloud import WordCloud
    WORDCLOUD = True
except Exception:
    WORDCLOUD = False

PROJECT_ROOT = Path(__file__).resolve().parents[2]
# We’ll search these directories in order
EXPORTS_CANDIDATES = [
    PROJECT_ROOT / "app" / "static" / "exports",
    PROJECT_ROOT / "Notebooks" / "app" / "static" / "exports",
    PROJECT_ROOT / "app" / "static" / "analytics",  # older path variant
]
DATA_DIR = PROJECT_ROOT / "Dataset"

def _existing_dirs(paths: List[Path]) -> List[Path]:
    return [p for p in paths if p.exists()]

def _read_csv_any(name: str) -> Optional[pd.DataFrame]:
    for base in _existing_dirs(EXPORTS_CANDIDATES):
        p = base / name
        if p.exists():
            try:
                return pd.read_csv(p)
            except Exception:
                try:
                    return pd.read_excel(p)
                except Exception:
                    pass
    return None

def _read_pickle_text_any(name: str) -> Optional[str]:
    import pickle
    for base in _existing_dirs(EXPORTS_CANDIDATES + [PROJECT_ROOT / "Saved_Model"]):
        p = base / name
        if p.exists():
            try:
                obj = pickle.load(open(p, "rb"))
                return obj if isinstance(obj, str) else str(obj)
            except Exception:
                pass
    return None

# ---------- column synonym helpers ----------
def find_col(columns: List[str], candidates: List[str]) -> Optional[str]:
    cols_lower = {c.lower(): c for c in columns}
    for cand in candidates:
        if cand in cols_lower:
            return cols_lower[cand]
    norm = {c.lower().replace(" ", "").replace("_", ""): c for c in columns}
    for cand in candidates:
        k = cand.replace(" ", "").replace("_", "")
        if k in norm:
            return norm[k]
    return None

def get_cols(df: pd.DataFrame, role: str) -> Optional[str]:
    synonyms = {
        "sector": ["sector", "sector_name", "area", "location"],
        "lat": ["latitude", "lat", "lat_deg"],
        "lon": ["longitude", "lon", "lng", "long", "lon_deg"],
        "price": ["price", "final_price", "price_in_inr", "priceinr", "price_crore", "pricecrore"],
        "pps": ["price_per_sqft", "pricepersqft", "price_per_sqfeet", "pps", "avg_pps", "avg_price_per_sqft", "ppsf"],
        "area": ["built_up_area", "builtup_area", "area", "sqft", "carpet_area", "super_area"],
        "bhk": ["bedRoom", "bedroom", "bhk", "BHK", "rooms"],
        "ptype": ["property_type", "type", "propertyType", "property"],
    }
    return find_col(list(df.columns), synonyms[role])

def to_num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")

def clip99(s: pd.Series) -> pd.Series:
    s = to_num(s)
    if s.isna().all():
        return s
    return s.clip(upper=float(s.quantile(0.99)))

# ---------- sector summary fallback if file missing ----------
def _parse_latlon(df_lat: pd.DataFrame) -> pd.DataFrame:
    import re
    def _parse(s):
        if pd.isna(s):
            return np.nan, np.nan
        s_raw = str(s)
        s_clean = s_raw.replace("°", "")
        nums = re.findall(r"[-+]?\d*\.\d+|[-+]?\d+", s_clean)
        lat = float(nums[0]) if len(nums) > 0 else np.nan
        lon = float(nums[1]) if len(nums) > 1 else np.nan
        if "S" in s_raw.upper():
            lat = -abs(lat)
        if "W" in s_raw.upper():
            lon = -abs(lon)
        return lat, lon

    if "coordinates" in df_lat.columns:
        lat, lon = zip(*df_lat["coordinates"].apply(_parse))
        df_lat["latitude"] = lat
        df_lat["longitude"] = lon
    return df_lat

def compute_sector_summary_from_dataset(df_clean: pd.DataFrame) -> Optional[pd.DataFrame]:
    lat_file = DATA_DIR / "latlong.csv"
    if not lat_file.exists():
        return None
    try:
        latlong = pd.read_csv(lat_file)
        latlong = _parse_latlon(latlong)
        sec_col = get_cols(df_clean, "sector")
        if sec_col is None:
            return None
        merged = df_clean.merge(
            latlong[["sector", "latitude", "longitude"]],
            left_on=sec_col, right_on="sector", how="left"
        )
        for c in ["price", "price_per_sqft", "built_up_area", "latitude", "longitude"]:
            if c in merged.columns:
                merged[c] = to_num(merged[c])
        group = merged.groupby("sector", as_index=False).agg(
            latitude=("latitude", "mean"),
            longitude=("longitude", "mean"),
            avg_price=("price", "mean") if "price" in merged.columns else ("latitude", "size"),
            avg_pps=("price_per_sqft", "mean") if "price_per_sqft" in merged.columns else ("latitude", "size"),
            avg_area=("built_up_area", "mean") if "built_up_area" in merged.columns else ("latitude", "size"),
            listings=("sector", "size"),
        )
        return group.dropna(subset=["latitude", "longitude"])
    except Exception:
        return None

# ---------- load dataframes ----------
def load_dataframes() -> Dict[str, Optional[pd.DataFrame]]:
    clean = _read_csv_any("gurgaon_cleaned_data.csv")
    # If not provided, try dataset default
    if clean is None:
        dataset_file = DATA_DIR / "gurgaon_properties_missing_value_imputation.csv"
        if dataset_file.exists():
            clean = pd.read_csv(dataset_file)

    sector = _read_csv_any("sector_summary.csv")
    corr = _read_csv_any("correlation_matrix.csv")

    # Fallback sector summary if file missing
    if sector is None and clean is not None:
        sector = compute_sector_summary_from_dataset(clean)

    return {"clean": clean, "sector": sector, "corr": corr}

# ---------- figures ----------
def build_figures() -> Dict[str, dict]:
    dfs = load_dataframes()
    df = dfs["clean"]
    sector = dfs["sector"]
    corr = dfs["corr"]

    charts: Dict[str, dict] = {}

    # 1) Sector map
    if sector is not None and len(sector):
        lat = get_cols(sector, "lat")
        lon = get_cols(sector, "lon")
        sec = get_cols(sector, "sector") or ("sector" if "sector" in sector.columns else None)
        color = get_cols(sector, "pps") or get_cols(sector, "price")
        size = get_cols(sector, "area")
        if lat and lon:
            for c in [lat, lon, color, size]:
                if c and c in sector.columns:
                    sector[c] = to_num(sector[c])
            fig = px.scatter_mapbox(
                sector.dropna(subset=[lat, lon]),
                lat=lat, lon=lon,
                color=color if color else None,
                size=size if size else None,
                size_max=28,
                color_continuous_scale=px.colors.cyclical.IceFire,
                zoom=10,
                mapbox_style="open-street-map",
                hover_name=sec if sec else None,
                title="Average Price per Sqft by Sector",
                height=520
            )
            charts["map_sector"] = json.loads(pio.to_json(fig))

    if df is None or not len(df):
        return charts

    price = get_cols(df, "price")
    area = get_cols(df, "area")
    bhk = get_cols(df, "bhk")
    ptype = get_cols(df, "ptype")
    pps = get_cols(df, "pps")
    sec = get_cols(df, "sector")

    # 2) Scatter: Area vs Price
    if area and price and bhk:
        tmp = df.dropna(subset=[area, price, bhk]).copy()
        if len(tmp) > 6000:
            tmp = tmp.sample(6000, random_state=42)
        tmp[price] = clip99(tmp[price])
        tmp[bhk] = to_num(tmp[bhk]).astype("Int64").astype(str)
        fig = px.scatter(tmp, x=area, y=price, color=bhk,
                         labels={"color": "BHK"}, title="Built-up Area vs Price", height=480)
        charts["scatter_area_price"] = json.loads(pio.to_json(fig))

    # 3) Pie: BHK distribution
    if bhk:
        vc = to_num(df[bhk]).dropna().astype(int).value_counts().reset_index()
        if len(vc):
            vc.columns = ["BHK", "count"]
            fig = px.pie(vc, names="BHK", values="count", title="BHK Distribution", height=420)
            charts["pie_bhk"] = json.loads(pio.to_json(fig))

    # 4) Box: Price range by BHK (≤ 4)
    if bhk and price:
        bx = df.copy()
        bx[bhk] = to_num(bx[bhk])
        bx = bx[bx[bhk] <= 4].dropna(subset=[bhk, price])
        if len(bx):
            bx[bhk] = bx[bhk].astype(int).astype(str)
            bx[price] = clip99(bx[price])
            fig = px.box(bx, x=bhk, y=price, color=bhk,
                         title="Price Range by BHK (≤ 4 BHK)", height=420)
            charts["box_bhk_price"] = json.loads(pio.to_json(fig))

    # 5) Histogram: price by property_type
    if price and ptype:
        h = df.dropna(subset=[price, ptype]).copy()
        if len(h):
            h[price] = clip99(h[price])
            fig = px.histogram(h, x=price, color=ptype, nbins=50,
                               barmode="overlay", opacity=0.65,
                               title="Price Distribution by Property Type", height=420)
            charts["hist_price_type"] = json.loads(pio.to_json(fig))

    # 6) Sunburst: property_type → BHK
    if ptype and bhk:
        sb = df.dropna(subset=[ptype, bhk]).copy()
        if len(sb):
            sb["BHK"] = to_num(sb[bhk]).astype("Int64").astype(str) + " BHK"
            sb["value"] = 1
            fig = px.sunburst(sb, path=[ptype, "BHK"], values="value",
                              title="Composition: Property Type → BHK", height=450)
            charts["sunburst_type_bhk"] = json.loads(pio.to_json(fig))

    # 7) Top sectors by avg price/sqft
    if sec and pps:
        top = df.dropna(subset=[sec, pps]).copy()
        if len(top):
            top = top.groupby(sec, as_index=False)[pps].mean().sort_values(pps, ascending=False).head(15)
            fig = px.bar(top, x=sec, y=pps, title="Top Sectors by Avg Price per Sqft", height=420)
            fig.update_layout(xaxis_tickangle=-40)
            charts["bar_top_sectors_pps"] = json.loads(pio.to_json(fig))

    # 8) Correlation heatmap (use provided or compute)
    df_corr = dfs["corr"]
    heatmap_df = None
    if df_corr is not None and df_corr.shape[0] == df_corr.shape[1]:
        heatmap_df = df_corr
    else:
        num_df = df.select_dtypes(include=[np.number])
        if num_df.shape[1] >= 2:
            heatmap_df = num_df.corr()

    if heatmap_df is not None and heatmap_df.shape[0] and heatmap_df.shape[1]:
        fig = px.imshow(heatmap_df, text_auto=False, aspect="auto",
                        color_continuous_scale="RdBu", title="Correlation Matrix", height=520)
        charts["heatmap_corr"] = json.loads(pio.to_json(fig))

    return charts

def build_wordcloud_base64() -> Optional[str]:
    if not WORDCLOUD:
        return None
    text = _read_pickle_text_any("feature_text.pkl")
    if not text:
        return None
    from io import BytesIO
    import matplotlib.pyplot as plt
    wc = WordCloud(width=1000, height=600, background_color="white").generate(text)
    buf = BytesIO()
    plt.figure(figsize=(10,6))
    plt.imshow(wc, interpolation="bilinear"); plt.axis("off"); plt.tight_layout()
    plt.savefig(buf, format="png", dpi=140); plt.close()
    buf.seek(0)
    import base64
    return base64.b64encode(buf.read()).decode("utf-8")

# --------- quick debug helper ----------
def debug_check():
    print("Project root:", PROJECT_ROOT)
    print("Search exports in:")
    for p in EXPORTS_CANDIDATES:
        print(" -", p, "exists:", p.exists())
    dfs = load_dataframes()
    for k, v in dfs.items():
        print(f"{k}: exists={v is not None}", "shape=" + (str(v.shape) if isinstance(v, pd.DataFrame) else "N/A"))
        if isinstance(v, pd.DataFrame):
            print("  columns:", list(v.columns)[:20])