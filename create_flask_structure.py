import os

# ------------------------------
# Define project structure
# ------------------------------
structure = {
    "app": {
        "routes": [
            "__init__.py",
            "home_routes.py",
            "prediction_routes.py",
            "recommendation_routes.py",
            "analytics_routes.py",
            "insights_routes.py",
        ],
        "templates": [
            "base.html",
            "home.html",
            "prediction.html",
            "recommendation.html",
            "analytics.html",
            "insights.html",
        ],
        "static/css": ["style.css"],
        "static/js": ["main.js"],
        "static/images": [],
        "utils": ["model_loader.py", "data_helper.py", "recommendation_engine.py"],
        "config.py": "",
        "__init__.py": "",
    },
    "requirements.txt": "",
    "run.py": "",
}

# ------------------------------
# Create directories and files
# ------------------------------
def create_structure(base_path, struct):
    for key, value in struct.items():
        path = os.path.join(base_path, key)

        # if value is dict -> create folder
        if isinstance(value, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, value)
        elif isinstance(value, list):
            os.makedirs(path, exist_ok=True)
            for filename in value:
                file_path = os.path.join(path, filename)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("")
        else:
            # single file
            file_path = os.path.join(base_path, key)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("")

# ------------------------------
# Write file contents
# ------------------------------

def write_files(base_path):
    # run.py
    with open(os.path.join(base_path, "run.py"), "w", encoding="utf-8") as f:
        f.write('''from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
''')

    # app/__init__.py
    with open(os.path.join(base_path, "app/__init__.py"), "w", encoding="utf-8") as f:
        f.write('''from flask import Flask
from .routes.home_routes import home_bp
from .routes.prediction_routes import prediction_bp
from .routes.recommendation_routes import recommendation_bp
from .routes.analytics_routes import analytics_bp
from .routes.insights_routes import insights_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(home_bp)
    app.register_blueprint(prediction_bp, url_prefix="/prediction")
    app.register_blueprint(recommendation_bp, url_prefix="/recommendation")
    app.register_blueprint(analytics_bp, url_prefix="/analytics")
    app.register_blueprint(insights_bp, url_prefix="/insights")
    return app
''')

    # routes
    routes_path = os.path.join(base_path, "app/routes")
    routes = {
        "home_routes.py": '''from flask import Blueprint, render_template
home_bp = Blueprint("home", __name__)
@home_bp.route("/")
def home():
    return render_template("home.html")
''',

        "prediction_routes.py": '''from flask import Blueprint, render_template, request
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
''',

        "recommendation_routes.py": '''from flask import Blueprint, render_template
recommendation_bp = Blueprint("recommendation", __name__)
@recommendation_bp.route("/")
def recommendation():
    return render_template("recommendation.html")
''',

        "analytics_routes.py": '''from flask import Blueprint, render_template
analytics_bp = Blueprint("analytics", __name__)
@analytics_bp.route("/")
def analytics():
    return render_template("analytics.html")
''',

        "insights_routes.py": '''from flask import Blueprint, render_template
insights_bp = Blueprint("insights", __name__)
@insights_bp.route("/")
def insights():
    return render_template("insights.html")
'''
    }

    for filename, content in routes.items():
        with open(os.path.join(routes_path, filename), "w", encoding="utf-8") as f:
            f.write(content)

    # templates
    templates_path = os.path.join(base_path, "app/templates")
    templates = {
        "base.html": '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Real Estate Insights</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark px-3">
        <a class="navbar-brand" href="/">🏙️ Real Estate Platform</a>
        <div class="navbar-nav ms-auto">
            <a class="nav-link" href="/prediction">Prediction</a>
            <a class="nav-link" href="/recommendation">Recommendation</a>
            <a class="nav-link" href="/analytics">Analytics</a>
            <a class="nav-link" href="/insights">Insights</a>
        </div>
    </nav>
    <div class="content">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
''',

        "home.html": '''{% extends "base.html" %}
{% block content %}
<div class="container text-center mt-5">
    <h1>🏙️ Real Estate Insights Platform</h1>
    <p>Choose a module to explore:</p>
    <div class="btn-group mt-4">
        <a href="/prediction" class="btn btn-primary">Price Prediction</a>
        <a href="/recommendation" class="btn btn-secondary">Property Recommendation</a>
        <a href="/analytics" class="btn btn-success">Analytics Dashboard</a>
        <a href="/insights" class="btn btn-info">Insights Module</a>
    </div>
</div>
{% endblock %}
''',

        "prediction.html": '''{% extends "base.html" %}
{% block content %}
<div class="container mt-5">
  <h2>🏠 Price Prediction</h2>
  <form method="POST" class="mt-4">
    <div class="form-group mb-3">
      <label>Bedrooms:</label>
      <input type="number" name="bedRoom" class="form-control" required>
    </div>
    <div class="form-group mb-3">
      <label>Bathrooms:</label>
      <input type="number" name="bathroom" class="form-control" required>
    </div>
    <div class="form-group mb-3">
      <label>Built Up Area (sq ft):</label>
      <input type="number" name="built_up_area" class="form-control" required>
    </div>
    <button class="btn btn-primary">Predict</button>
  </form>

  {% if prediction %}
  <div class="alert alert-success mt-4">
    💰 Predicted Price: ₹{{ prediction }} Lakhs
  </div>
  {% endif %}
</div>
{% endblock %}
''',

        "recommendation.html": '''{% extends "base.html" %}
{% block content %}
<div class="container mt-5 text-center">
    <h2>🏡 Property Recommendation</h2>
    <p>This page will show recommended properties based on user preferences.</p>
</div>
{% endblock %}
''',

        "analytics.html": '''{% extends "base.html" %}
{% block content %}
<div class="container mt-5 text-center">
    <h2>📊 Analytics Dashboard</h2>
    <p>Charts and visualizations of property trends will go here.</p>
</div>
{% endblock %}
''',

        "insights.html": '''{% extends "base.html" %}
{% block content %}
<div class="container mt-5 text-center">
    <h2>💡 Insights Module</h2>
    <p>Insights and data-driven analysis will appear here.</p>
</div>
{% endblock %}
'''
    }

    for filename, content in templates.items():
        with open(os.path.join(templates_path, filename), "w", encoding="utf-8") as f:
            f.write(content)

    # CSS
    with open(os.path.join(base_path, "app/static/css/style.css"), "w", encoding="utf-8") as f:
        f.write('''body {background-color: #f5f7fa;font-family: 'Inter', sans-serif;}
h1, h2 {font-weight: 600;}
.btn {border-radius: 12px; padding: 10px 20px;}
.navbar {box-shadow: 0 2px 6px rgba(0,0,0,0.1);}
''')

    # requirements.txt
    with open(os.path.join(base_path, "requirements.txt"), "w", encoding="utf-8") as f:
        f.write("flask\npandas\njoblib\nscikit-learn\n")

# ------------------------------
# Run script
# ------------------------------
if __name__ == "__main__":
    base_path = os.getcwd()
    print(f"📁 Creating Flask structure under: {base_path}")
    create_structure(base_path, structure)
    write_files(base_path)
    print("✅ Flask project structure created successfully!")
