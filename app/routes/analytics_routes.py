# app/routes/analytics_routes.py

from flask import Blueprint, render_template, request, current_app, abort

from app.utils.analytics_loader import (
    load_visualization_data,
    build_all_figures,
    get_sector_options,
    generate_wordcloud_base64,
)

analytics_bp = Blueprint("analytics", __name__, url_prefix="/analytics")


@analytics_bp.route("/", methods=["GET", "POST"])
def analytics():
    try:
        df, group_df, sector_feature_map = load_visualization_data()
        current_app.logger.info(f"[analytics] df rows: {len(df)}, group_df rows: {len(group_df)}")
    except Exception as e:
        current_app.logger.exception("Failed to load analytics data", exc_info=e)
        abort(500, description=f"Failed to load analytics data: {e}")

    figs = build_all_figures(df, group_df)

    sectors = get_sector_options(sector_feature_map, df)
    selected_sector = request.values.get("sector", sectors[0] if sectors else None)
    sector_text = sector_feature_map.get(selected_sector, "") if selected_sector else ""
    wordcloud_img = generate_wordcloud_base64(sector_text)

    return render_template(
        "analytics.html",
        # Core figs
        map_html=figs["map_html"],
        scatter_html=figs["scatter_html"],
        box_html=figs["box_html"],
        pie_html=figs["pie_html"],
        # New insights
        hist_psf_html=figs["hist_psf_html"],
        sector_bar_psf_html=figs["sector_bar_psf_html"],
        violin_bhk_psf_html=figs["violin_bhk_psf_html"],
        area_psf_scatter_html=figs["area_psf_scatter_html"],
        luxury_psf_scatter_html=figs["luxury_psf_scatter_html"],
        corr_heatmap_html=figs["corr_heatmap_html"],
        # Wordcloud
        sectors=sectors,
        selected_sector=selected_sector,
        wordcloud_image_data=wordcloud_img,
    )