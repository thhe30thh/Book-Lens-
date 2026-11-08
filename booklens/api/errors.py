from flask import jsonify, request
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        if request.path.startswith("/api/"):
            return jsonify({
                "error": error.name,
                "message": error.description,
                "status": error.code
            }), error.code

        return error