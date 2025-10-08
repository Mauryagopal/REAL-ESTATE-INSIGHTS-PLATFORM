from flask import Flask
from .config import Config
from .utils.data_helper import ensure_schema_compatibility

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Validate schema once at startup
    try:
        ensure_schema_compatibility()
    except Exception as e:
        # You can log this and still boot, or raise to stop the app
        raise

    from .routes.home_routes import home_bp
    from .routes.prediction_routes import prediction_bp
    app.register_blueprint(home_bp)
    app.register_blueprint(prediction_bp)

    return app