from flask import Blueprint

api_bp = Blueprint("api", __name__)

from booklens.api.health import health_bp

api_bp.register_blueprint(health_bp)