# app/__init__.py
from flask import Flask
from .config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from .routes.home_routes import home_bp
    from .routes.prediction_routes import prediction_bp
    from .routes.analytics_routes import analytics_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(prediction_bp)
    app.register_blueprint(analytics_bp)
    return app