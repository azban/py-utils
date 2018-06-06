from __future__ import absolute_import

import logging

from flask import (
    Flask,
    jsonify,
)
from schematics import Model
from schematics.types import (
    BaseType,
    IntType,
    StringType,
)
from werkzeug.exceptions import (
    BadRequest,
    InternalServerError,
    MethodNotAllowed,
    NotFound,
)


class HTTPApiError(Exception):
    status_code = 400
    code = NotImplemented
    data = None


class HTTPServerError(HTTPApiError):
    status_code = 500
    code = 'server-error'


class HTTPNotFoundError(HTTPApiError):
    status_code = 404
    code = 'not-found'


class HTTPMethodNotAllowedError(HTTPApiError):
    status_code = 405
    code = 'method-not-allowed'


class HTTPValidationError(HTTPApiError):
    status_code = 400
    code = 'validation-error'

    def __init__(self, data):
        self.data = data

    @classmethod
    def from_data_error(cls, error):
        return cls(error.to_primitive())


class HTTPInvalidJSONError(HTTPApiError):
    status_code = 400
    code = 'invalid-json'


class HTTPApiErrorResponse(Model):
    status_code = IntType(required=True)
    code = StringType(required=True, min_length=1)
    data = BaseType()

    @classmethod
    def from_error(cls, error):
        return cls({
            'status_code': error.status_code,
            'code': error.code,
            'data': error.data,
        })


def create_app(name):
    app = Flask(name)

    @app.errorhandler(HTTPApiError)
    def handle_http_api_error(error):
        error_response = HTTPApiErrorResponse.from_error(error)
        error_response.validate()
        response = jsonify(error_response.to_primitive())
        response.status_code = error_response.status_code
        return response

    @app.errorhandler(Exception)
    def handle_uncaught_exception(exception):
        logging.exception(exception)
        return handle_http_api_error(HTTPServerError)

    @app.errorhandler(BadRequest)
    def handle_bad_request(exception):
        if exception.description.startswith('Failed to decode JSON object'):
            return handle_http_api_error(HTTPInvalidJSONError)
        else:
            return handle_uncaught_exception(exception)

    @app.errorhandler(NotFound)
    def handle_not_found(_):
        return handle_http_api_error(HTTPNotFoundError)

    @app.errorhandler(MethodNotAllowed)
    def handle_method_not_allowed(_):
        return handle_http_api_error(HTTPMethodNotAllowedError)

    @app.errorhandler(InternalServerError)
    def handle_uncaught_exception(_):
        return handle_http_api_error(HTTPServerError)

    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = '*'
        return response

    return app
