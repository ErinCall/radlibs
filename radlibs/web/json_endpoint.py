from __future__ import unicode_literals

import json
from functools import wraps
from flask import make_response
from werkzeug.exceptions import BadRequestKeyError


def json_endpoint(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            response = fn(*args, **kwargs)
        except BadRequestKeyError as e:
            response = error_response("missing param '{0}'".format(e.message))
        if type(response) in [list, dict]:
            response = json.dumps(response)

        if type(response) in [unicode, str]:
            response = make_response(response)
        return response
    return wrapper


def error_response(error):
    return {'status': 'error', 'error': error}
