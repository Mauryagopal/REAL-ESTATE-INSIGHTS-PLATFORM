from flask import Blueprint, render_template, flash
from ..utils.analytics_loader import build_figures, build_wordcloud_base64

analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.route("/analytics")
def analytics():
    try:
        charts = build_figures()
    except Exception as e:
        charts = {}
        flash(f"Failed to build charts: {e}", "danger")

    wc_b64 = None
    try:
        wc_b64 = build_wordcloud_base64()
    except Exception:
        wc_b64 = None

    return render_template("analytics.html", charts=charts, wc_b64=wc_b64)