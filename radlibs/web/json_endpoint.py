from __future__ import unicode_literals

import json
from functools import wraps
from flask import make_response


def json_endpoint(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        response = fn(*args, **kwargs)
        if type(response) in [list, dict]:
            response = json.dumps(response)

        if type(response) in [unicode, str]:
            response = make_response(response)
        return response
    return wrapper


def error_response(error):
    return {'status': 'error', 'error': error}
