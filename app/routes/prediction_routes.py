from flask import Blueprint, render_template, request, flash
from ..utils.model_loader import get_model
from ..utils.data_helper import form_to_dataframe, convert_crore_to_inr, format_price

prediction_bp = Blueprint("prediction", __name__)

@prediction_bp.route("/predict", methods=["GET", "POST"])
def predict():
    result = None
    if request.method == "POST":
        try:
            df = form_to_dataframe(request.form.to_dict())
            model = get_model()
            y_crore = float(model.predict(df)[0])   # model predicts crore
            amount_in_inr = convert_crore_to_inr(y_crore)
            fp = format_price(amount_in_inr)

            result = {
                "display": fp["main"],  # e.g., ₹1.14 Cr
                "breakdown": {"inr": fp["inr"], "lakh": fp["lakh"], "crore": fp["crore"]},
                "raw": y_crore,  # show raw crore for debugging
            }
        except Exception as e:
            flash(f"Prediction failed: {e}", "danger")

    return render_template("prediction.html", result=result)