from flask import jsonify


class APIError(Exception):
    status_code = 500
    message = 'Internal server error'

    def __init__(self, message=None, status_code=None):
        if message:
            self.message = message
        if status_code:
            self.status_code = status_code


class NotFoundError(APIError):
    status_code = 404
    message = 'Resource not found'


class ValidationError(APIError):
    status_code = 400
    message = 'Validation error'


class ConflictError(APIError):
    status_code = 409
    message = 'Conflict'


class UnauthorizedError(APIError):
    status_code = 401
    message = 'Unauthorized'


class ForbiddenError(APIError):
    status_code = 403
    message = 'Forbidden'


def register_error_handlers(app):
    @app.after_request
    def normalize_pydantic_422(response):
        if response.status_code == 422:
            data = response.get_json(silent=True)
            if data and 'detail' in data:
                errors = data['detail']
                if errors:
                    first = errors[0]
                    loc = [str(l) for l in first.get('loc', [])[1:]]
                    field = '.'.join(loc)
                    msg = first.get('msg', 'Validation failed')
                    message = f'{field}: {msg}' if field else msg
                else:
                    message = 'Request validation failed'
                return jsonify({
                    'error': 'ValidationError',
                    'message': message,
                    'status_code': 422
                }), 422
        return response

    @app.errorhandler(APIError)
    def handle_api_error(error):
        return jsonify({
            'error': error.__class__.__name__,
            'message': error.message,
            'status_code': error.status_code
        }), error.status_code

    @app.errorhandler(400)
    def handle_400(error):
        return jsonify({
            'error': 'BadRequest',
            'message': 'Bad request',
            'status_code': 400
        }), 400

    @app.errorhandler(404)
    def handle_404(error):
        return jsonify({
            'error': 'NotFound',
            'message': 'The requested resource was not found',
            'status_code': 404
        }), 404

    @app.errorhandler(405)
    def handle_405(error):
        return jsonify({
            'error': 'MethodNotAllowed',
            'message': 'Method not allowed',
            'status_code': 405
        }), 405

    @app.errorhandler(500)
    def handle_500(error):
        return jsonify({
            'error': 'InternalServerError',
            'message': 'An unexpected error occurred',
            'status_code': 500
        }), 500
