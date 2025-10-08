# app/routes/__init__.py
from .home_routes import home_bp
from .prediction_routes import prediction_bp

__all__ = ["home_bp", "prediction_bp"]