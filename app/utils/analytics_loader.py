# app/utils/analytics_loader.py
from __future__ import annotations
import json
import base64
from io import BytesIO
from pathlib import Path
from typing import Dict, Optional

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

EXPORTS_DIR = Path(__file__).resolve().parents[2] / "app" / "static" / "exports"

def _read_csv(name: str) -> Optional[pd.DataFrame]:
    p = EXPORTS_DIR / name
    if not p.exists():
        return None
    return pd.read_csv(p)

def _read_pickle_text(name: str) -> Optional[str]:
    p = EXPORTS_DIR / name
    if not p.exists():
        return None
    import pickle
    with open(p, "rb") as f:
        obj = pickle.load(f)
    return obj if isinstance(obj, str) else str(obj)

def load_dataframes() -> Dict[str, pd.DataFrame]:
    dfs = {
        "clean": _read_csv("gurgaon_cleaned_data.csv"),
        "sector": _read_csv("sector_summary.csv"),
        "corr": _read_csv("correlation_matrix.csv"),
    }
    return dfs

def _num(x):
    return pd.to_numeric(x, errors="coerce")

def _clip99(s: pd.Series):
    if s is None: 
        return s
    if not np.issubdtype(s.dtype, np.number):
        s = pd.to_numeric(s, errors="coerce")
    up = s.quantile(0.99)
    return s.clip(upper=up)

def build_figures() -> Dict[str, dict]:
    dfs = load_dataframes()
    df = dfs["clean"]
    sector = dfs["sector"]
    corr = dfs["corr"]

    charts: Dict[str, dict] = {}

    # 1) Sector Map
    if sector is not None and {"latitude","longitude"}.issubset(sector.columns):
        # Expect columns: sector, latitude, longitude, avg_price, avg_pps, avg_area, listings
        # Fallbacks if names differ
        lat_col = "latitude"
        lon_col = "longitude"
        color_col = "avg_pps" if "avg_pps" in sector.columns else "price_per_sqft"
        size_col = "avg_area" if "avg_area" in sector.columns else "built_up_area"

        for c in [color_col, size_col, lat_col, lon_col]:
            if c in sector.columns:
                sector[c] = _num(sector[c])

        sector_map = px.scatter_mapbox(
            sector.dropna(subset=[lat_col, lon_col]),
            lat=lat_col,
            lon=lon_col,
            color=color_col if color_col in sector.columns else None,
            size=size_col if size_col in sector.columns else None,
            size_max=28,
            color_continuous_scale=px.colors.cyclical.IceFire,
            zoom=10,
            mapbox_style="open-street-map",
            hover_name="sector" if "sector" in sector.columns else None,
            hover_data={color_col:":.0f"} if color_col in sector.columns else None,
            title="Average Price per Sqft by Sector",
            height=520
        )
        charts["map_sector"] = json.loads(pio.to_json(sector_map))

    if df is not None:
        # Ensure numerics
        for c in ["price","built_up_area","price_per_sqft","bedRoom"]:
            if c in df.columns:
                df[c] = _num(df[c])

        # 2) Scatter: Area vs Price (colored by BHK)
        if {"built_up_area","price","bedRoom"}.issubset(df.columns):
            scat = df.dropna(subset=["built_up_area","price","bedRoom"]).copy()
            if len(scat) > 6000:
                scat = scat.sample(6000, random_state=42)
            scat["price"] = _clip99(scat["price"])
            scat["bedRoom"] = scat["bedRoom"].astype(int).astype(str)
            fig = px.scatter(
                scat,
                x="built_up_area", y="price", color="bedRoom",
                labels={"color":"BHK"},
                title="Built-up Area vs Price",
                height=480
            )
            charts["scatter_area_price"] = json.loads(pio.to_json(fig))

        # 3) Pie: BHK distribution
        if "bedRoom" in df.columns:
            vc = df["bedRoom"].dropna().astype(int).value_counts().reset_index()
            vc.columns = ["bedRoom","count"]
            fig = px.pie(vc, names="bedRoom", values="count", title="BHK Distribution", height=420)
            charts["pie_bhk"] = json.loads(pio.to_json(fig))

        # 4) Box: Price range by BHK (≤4)
        if {"bedRoom","price"}.issubset(df.columns):
            bx = df[df["bedRoom"].le(4)].dropna(subset=["price","bedRoom"]).copy()
            bx["bedRoom"] = bx["bedRoom"].astype(int).astype(str)
            bx["price"] = _clip99(bx["price"])
            fig = px.box(bx, x="bedRoom", y="price", color="bedRoom",
                         title="Price Range by BHK (≤ 4 BHK)", height=420)
            charts["box_bhk_price"] = json.loads(pio.to_json(fig))

        # 5) Histogram: price by property_type
        if {"price","property_type"}.issubset(df.columns):
            h = df.dropna(subset=["price","property_type"]).copy()
            h["price"] = _clip99(h["price"])
            fig = px.histogram(h, x="price", color="property_type", nbins=50,
                               barmode="overlay", opacity=0.65,
                               title="Price Distribution by Property Type", height=420)
            charts["hist_price_type"] = json.loads(pio.to_json(fig))

        # 6) Sunburst: property_type → BHK
        if {"property_type","bedRoom"}.issubset(df.columns):
            sb = df.dropna(subset=["property_type","bedRoom"]).copy()
            sb["BHK"] = sb["bedRoom"].astype(int).astype(str) + " BHK"
            sb["value"] = 1
            fig = px.sunburst(sb, path=["property_type","BHK"], values="value",
                              title="Composition: Property Type → BHK", height=450)
            charts["sunburst_type_bhk"] = json.loads(pio.to_json(fig))

    # 7) Correlation heatmap
    if corr is not None:
        corr_df = corr.copy()
        # If corr is a “long”/flat CSV, try pivot; else assume square
        try:
            if set(["feature","index","value"]).issubset(corr_df.columns):
                corr_df = corr_df.pivot(index="index", columns="feature", values="value")
        except Exception:
            pass
        fig = px.imshow(corr_df, text_auto=False, aspect="auto",
                        color_continuous_scale="RdBu",
                        title="Correlation Matrix", height=520)
        fig.update_layout(coloraxis_showscale=True)
        charts["heatmap_corr"] = json.loads(pio.to_json(fig))

    return charts

def build_wordcloud_base64() -> Optional[str]:
    if not WORDCLOUD:
        return None
    text = _read_pickle_text("feature_text.pkl")
    if not text:
        return None
    wc = WordCloud(width=1000, height=600, background_color="white").generate(text)
    import matplotlib.pyplot as plt
    buf = BytesIO()
    plt.figure(figsize=(10,6))
    plt.imshow(wc, interpolation="bilinear"); plt.axis("off"); plt.tight_layout()
    plt.savefig(buf, format="png", dpi=140); plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")