from flask import Blueprint, render_template, request, flash
from ..utils.model_loader import get_model, get_allowed_values, get_numeric_hints
from ..utils.data_helper import validate_and_prepare, convert_crore_to_inr, format_price

prediction_bp = Blueprint("prediction", __name__)

@prediction_bp.route("/predict", methods=["GET", "POST"])
def predict():
    choices = get_allowed_values()
    hints = get_numeric_hints()
    result = None
    errors = []
    form_state = {k: "" for k in (
        ["bedRoom","bathroom","built_up_area","servant_room","store_room",
         "property_type","sector","balcony","agePossession",
         "furnishing_type","luxury_category","floor_category"]
    )}

    if request.method == "POST":
        form_state.update(request.form.to_dict())
        df, errors, _clean = validate_and_prepare(form_state)
        if not errors:
            try:
                model = get_model()
                y_crore = float(model.predict(df)[0])  # model outputs crore
                amount_in_inr = convert_crore_to_inr(y_crore)
                fp = format_price(amount_in_inr)
                result = {
                    "display": fp["main"],
                    "breakdown": {"inr": fp["inr"], "lakh": fp["lakh"], "crore": fp["crore"]},
                    "raw": y_crore,
                }
            except Exception as e:
                errors.append(f"Prediction failed: {e}")

        if errors:
            for e in errors:
                flash(e, "danger")

    return render_template("prediction.html", choices=choices, hints=hints, result=result, form_state=form_state)