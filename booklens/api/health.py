from flask import Blueprint, current_app, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "booklens",
        "version": "0.1.0",
        "environment": current_app.config.get(
            "BOOKLENS_ENV",
            "development"
        )
    })