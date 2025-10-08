# app/utils/analytics_loader.py

from __future__ import annotations

import io
import base64
from pathlib import Path
from typing import Dict, Tuple, List

import pandas as pd
import plotly.express as px
from flask import current_app

# Headless matplotlib for servers
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from wordcloud import WordCloud


def _resolve_data_file(filename: str) -> Path:
    """
    Look for files in:
      1) app/static/exports/{filename}
      2) exported_data/{filename}
    """
    app_root = Path(current_app.root_path)  # .../app
    candidates = [
        app_root / "static" / "exports" / filename,
        app_root.parent / "exported_data" / filename,
    ]
    for p in candidates:
        if p.exists():
            return p.resolve()
    raise FileNotFoundError(f"Could not find {filename} in: {', '.join(str(c) for c in candidates)}")


def load_visualization_data() -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, str]]:
    """
    Your files and columns:
    - grouped_sector_data.csv (map):
        sector, price, price_per_sqft, built_up_area, latitude, longitude
    - data_viz_full.csv (plots):
        property_type, sector, society, price, price_per_sqft, bedRoom, built_up_area,
        bathroom, balcony, floorNum, facing, agePossession, luxury_score, latitude, longitude, ...
    - sector_feature_map.pkl (wordcloud)
    """
    df_path = _resolve_data_file("data_viz_full.csv")
    grouped_path = _resolve_data_file("grouped_sector_data.csv")
    sector_map_path = _resolve_data_file("sector_feature_map.pkl")

    # Load
    df = pd.read_csv(df_path, encoding="utf-8-sig")
    group_df = pd.read_csv(grouped_path, encoding="utf-8-sig")

    import pickle
    with open(sector_map_path, "rb") as f:
        sector_feature_map = pickle.load(f)

    # Coerce only what we need
    for col in [
        "built_up_area",
        "price",
        "bedRoom",
        "price_per_sqft",
        "bathroom",
        "balcony",
        "floorNum",
        "luxury_score",
    ]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in ["latitude", "longitude", "price_per_sqft", "built_up_area", "price"]:
        if col in group_df.columns:
            group_df[col] = pd.to_numeric(group_df[col], errors="coerce")

    return df, group_df, sector_feature_map


def _fig_to_html(fig) -> str:
    # Include Plotly per figure to avoid any script-order issues
    return fig.to_html(full_html=False, include_plotlyjs="cdn")


# Existing figures
def build_scatter_map(group_df: pd.DataFrame) -> str:
    required = ["latitude", "longitude", "price_per_sqft"]
    if group_df.empty or not all(c in group_df.columns for c in required):
        return "<div class='alert alert-info mb-0'>No map data available.</div>"

    fig = px.scatter_mapbox(
        group_df,
        lat="latitude",
        lon="longitude",
        color="price_per_sqft",
        size="built_up_area" if "built_up_area" in group_df.columns else None,
        hover_name="sector" if "sector" in group_df.columns else None,
        color_continuous_scale=px.colors.cyclical.IceFire,
        zoom=10,
        mapbox_style="open-street-map",
        title="Average Price per Sqft by Sector",
    )
    fig.update_layout(height=520, margin=dict(l=0, r=0, t=40, b=0))
    return _fig_to_html(fig)


def build_scatter_plot(df: pd.DataFrame) -> str:
    if not {"built_up_area", "price"}.issubset(df.columns):
        return "<div class='alert alert-warning mb-0'>Missing built_up_area or price in data_viz_full.csv</div>"
    sub = df.dropna(subset=["built_up_area", "price"])
    if sub.empty:
        return "<div class='alert alert-info mb-0'>No rows for scatter (built_up_area & price).</div>"

    fig = px.scatter(
        sub,
        x="built_up_area",
        y="price",
        color="bedRoom" if "bedRoom" in sub.columns else None,
        labels={"built_up_area": "Built-up Area (sqft)", "price": "Price (Cr)"},
        title="Built-up Area vs Price",
        opacity=0.8,
    )
    fig.update_layout(height=420, margin=dict(l=10, r=10, t=50, b=10))
    return _fig_to_html(fig)


def build_box_plot(df: pd.DataFrame) -> str:
    if not {"bedRoom", "price"}.issubset(df.columns):
        return "<div class='alert alert-warning mb-0'>Missing bedRoom or price in data_viz_full.csv</div>"
    sub = df.dropna(subset=["bedRoom", "price"])
    if sub.empty:
        return "<div class='alert alert-info mb-0'>No rows for BHK-wise price distribution.</div>"
    sub = sub[sub["bedRoom"] <= 8]

    fig = px.box(
        sub,
        x="bedRoom",
        y="price",
        points="outliers",
        labels={"bedRoom": "BHK", "price": "Price (Cr)"},
        title="BHK-wise Price Distribution",
    )
    fig.update_layout(height=420, margin=dict(l=10, r=10, t=50, b=10))
    return _fig_to_html(fig)


def build_pie_chart(df: pd.DataFrame) -> str:
    if "bedRoom" not in df.columns:
        return "<div class='alert alert-warning mb-0'>Missing bedRoom in data_viz_full.csv</div>"
    sub = df.dropna(subset=["bedRoom"]).copy()
    if sub.empty:
        return "<div class='alert alert-info mb-0'>No rows for bedroom distribution.</div>"
    sub["bedRoom"] = sub["bedRoom"].astype(int)
    agg = sub.groupby("bedRoom").size().reset_index(name="count").sort_values("bedRoom")

    fig = px.pie(
        agg,
        names="bedRoom",
        values="count",
        title="Bedroom Distribution",
        hole=0.35,
    )
    fig.update_layout(height=400, margin=dict(l=10, r=10, t=50, b=10))
    return _fig_to_html(fig)


# New insights
def build_hist_price_psf(df: pd.DataFrame) -> str:
    if "price_per_sqft" not in df.columns:
        return "<div class='alert alert-warning mb-0'>Missing price_per_sqft in data_viz_full.csv</div>"
    sub = df.dropna(subset=["price_per_sqft"])
    if sub.empty:
        return "<div class='alert alert-info mb-0'>No data for price per sqft distribution.</div>"

    fig = px.histogram(
        sub,
        x="price_per_sqft",
        nbins=50,
        color="property_type" if "property_type" in sub.columns else None,
        marginal="box",
        title="Price per Sqft Distribution",
        labels={"price_per_sqft": "Price per Sqft (₹)"},
        opacity=0.85,
    )
    fig.update_layout(height=420, margin=dict(l=10, r=10, t=50, b=10))
    return _fig_to_html(fig)


def build_sector_bar_psf(group_df: pd.DataFrame, top_n: int = 15) -> str:
    req = ["sector", "price_per_sqft"]
    if group_df.empty or not all(c in group_df.columns for c in req):
        return "<div class='alert alert-info mb-0'>No sector PSF data available.</div>"

    sub = group_df.dropna(subset=req)
    if sub.empty:
        return "<div class='alert alert-info mb-0'>No sector PSF data available after cleaning.</div>"

    # Top N sectors by PSF
    top = sub.sort_values("price_per_sqft", ascending=False).head(top_n)

    fig = px.bar(
        top,
        x="sector",
        y="price_per_sqft",
        title=f"Top {len(top)} Sectors by Avg Price per Sqft",
        labels={"price_per_sqft": "Avg PSF (₹)", "sector": "Sector"},
    )
    fig.update_layout(height=420, xaxis_tickangle=-35, margin=dict(l=10, r=10, t=50, b=100))
    return _fig_to_html(fig)


def build_violin_bhk_psf(df: pd.DataFrame) -> str:
    req = ["bedRoom", "price_per_sqft"]
    if not all(c in df.columns for c in req):
        return "<div class='alert alert-warning mb-0'>Requires bedRoom and price_per_sqft.</div>"
    sub = df.dropna(subset=req)
    if sub.empty:
        return "<div class='alert alert-info mb-0'>No data for PSF by BHK.</div>"
    sub = sub[sub["bedRoom"] <= 8]

    fig = px.violin(
        sub,
        x="bedRoom",
        y="price_per_sqft",
        box=True,
        points="outliers",
        title="Price per Sqft by BHK (Violin)",
        labels={"bedRoom": "BHK", "price_per_sqft": "PSF (₹)"},
    )
    fig.update_layout(height=420, margin=dict(l=10, r=10, t=50, b=10))
    return _fig_to_html(fig)


def build_area_psf_scatter(df: pd.DataFrame) -> str:
    req = ["built_up_area", "price_per_sqft"]
    if not all(c in df.columns for c in req):
        return "<div class='alert alert-warning mb-0'>Requires built_up_area and price_per_sqft.</div>"
    sub = df.dropna(subset=req)
    if sub.empty:
        return "<div class='alert alert-info mb-0'>No data for area vs PSF.</div>"

    fig = px.scatter(
        sub,
        x="built_up_area",
        y="price_per_sqft",
        color="bedRoom" if "bedRoom" in sub.columns else None,
        hover_name="society" if "society" in sub.columns else None,
        title="Built-up Area vs Price per Sqft",
        labels={"built_up_area": "Built-up Area (sqft)", "price_per_sqft": "PSF (₹)"},
        opacity=0.75,
    )
    fig.update_layout(height=420, margin=dict(l=10, r=10, t=50, b=10))
    return _fig_to_html(fig)


def build_luxury_psf_scatter(df: pd.DataFrame) -> str:
    req = ["luxury_score", "price_per_sqft"]
    if not all(c in df.columns for c in req):
        return "<div class='alert alert-warning mb-0'>Requires luxury_score and price_per_sqft.</div>"
    sub = df.dropna(subset=req)
    if sub.empty:
        return "<div class='alert alert-info mb-0'>No data for luxury vs PSF.</div>"

    fig = px.scatter(
        sub,
        x="luxury_score",
        y="price_per_sqft",
        color="property_type" if "property_type" in sub.columns else None,
        title="Luxury Score vs Price per Sqft",
        labels={"luxury_score": "Luxury Score", "price_per_sqft": "PSF (₹)"},
        opacity=0.75,
    )
    fig.update_layout(height=420, margin=dict(l=10, r=10, t=50, b=10))
    return _fig_to_html(fig)


def build_corr_heatmap(df: pd.DataFrame) -> str:
    # Focus on the most relevant numeric columns to keep the heatmap readable
    cols = [c for c in [
        "built_up_area", "price", "price_per_sqft", "bedRoom",
        "bathroom", "balcony", "floorNum", "luxury_score"
    ] if c in df.columns]
    if not cols:
        return "<div class='alert alert-warning mb-0'>No numeric columns available for correlation.</div>"

    sub = df[cols].copy()
    sub = sub.dropna(how="all")
    if sub.empty:
        return "<div class='alert alert-info mb-0'>No data for correlation heatmap.</div>"

    corr = sub.corr(numeric_only=True)
    fig = px.imshow(
        corr,
        text_auto=True,
        color_continuous_scale="RdBu",
        zmin=-1, zmax=1,
        aspect="auto",
        title="Feature Correlation Heatmap",
    )
    fig.update_layout(height=520, margin=dict(l=10, r=10, t=50, b=10))
    return _fig_to_html(fig)


def build_all_figures(df: pd.DataFrame, group_df: pd.DataFrame) -> Dict[str, str]:
    return {
        # Existing
        "map_html": build_scatter_map(group_df),
        "scatter_html": build_scatter_plot(df),
        "box_html": build_box_plot(df),
        "pie_html": build_pie_chart(df),
        # New insights
        "hist_psf_html": build_hist_price_psf(df),
        "sector_bar_psf_html": build_sector_bar_psf(group_df),
        "violin_bhk_psf_html": build_violin_bhk_psf(df),
        "area_psf_scatter_html": build_area_psf_scatter(df),
        "luxury_psf_scatter_html": build_luxury_psf_scatter(df),
        "corr_heatmap_html": build_corr_heatmap(df),
    }


def get_sector_options(sector_feature_map: Dict[str, str], df: pd.DataFrame | None = None) -> List[str]:
    sectors = list(sector_feature_map.keys()) if sector_feature_map else []
    if not sectors and df is not None and "sector" in df.columns:
        sectors = sorted(df["sector"].dropna().astype(str).unique().tolist())
    return sorted(sectors)


def generate_wordcloud_base64(sector_text: str, width: int = 700, height: int = 500) -> str:
    if not sector_text:
        sector_text = "No data available"
    wc = WordCloud(width=width, height=height, background_color="white").generate(sector_text)
    plt.figure(figsize=(width / 100, height / 100), dpi=100)
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", pad_inches=0.1)
    buf.seek(0)
    img_data = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()
    plt.close()
    return img_data