from flask import jsonify

def api_error(message, status_code=500):
    """Creates a standardized JSON error response."""
    return jsonify({
        "error": {
            "message": message,
            "type": "api_error"
        }
    }), status_code

def validation_error(message, status_code=400):
    """Creates a standardized JSON validation error response."""
    return jsonify({
        "error": {
            "message": message,
            "type": "validation_error"
        }
    }), status_code
