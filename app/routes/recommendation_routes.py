from flask import Blueprint, render_template
recommendation_bp = Blueprint("recommendation", __name__)
@recommendation_bp.route("/")
def recommendation():
    return render_template("recommendation.html")
