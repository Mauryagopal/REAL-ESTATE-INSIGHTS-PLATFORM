# app/__init__.py
from flask import Flask
from .config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register blueprints
    from .routes.home_routes import home_bp
    from .routes.prediction_routes import prediction_bp
    app.register_blueprint(home_bp)
    app.register_blueprint(prediction_bp)

    return app