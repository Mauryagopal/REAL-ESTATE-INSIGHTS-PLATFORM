from flask import Blueprint, render_template, request
import joblib, json
import pandas as pd

prediction_bp = Blueprint("prediction", __name__)
model = joblib.load("Saved_Model/gurgaon_price_model.joblib")
with open("Saved_Model/expected_columns.json", "r") as f:
    expected_columns = json.load(f)

@prediction_bp.route("/", methods=["GET", "POST"])
def prediction():
    prediction_result = None
    if request.method == "POST":
        form_data = request.form.to_dict()
        df = pd.DataFrame([form_data])
        df = df.reindex(columns=expected_columns, fill_value=0)
        prediction_result = round(model.predict(df)[0], 2)
    return render_template("prediction.html", prediction=prediction_result)
