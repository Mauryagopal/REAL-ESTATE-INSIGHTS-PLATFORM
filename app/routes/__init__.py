from flask import Flask

def create_app():
    app = Flask(__name__)

    # Register Blueprints
    from app.routes.home_routes import home_bp
    from app.routes.prediction_routes import prediction_bp
    from app.routes.recommendation_routes import recommendation_bp
    from app.routes.analytics_routes import analytics_bp
    from app.routes.insights_routes import insights_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(prediction_bp, url_prefix="/prediction")
    app.register_blueprint(recommendation_bp, url_prefix="/recommendation")
    app.register_blueprint(analytics_bp, url_prefix="/analytics")
    app.register_blueprint(insights_bp, url_prefix="/insights")

    return app
