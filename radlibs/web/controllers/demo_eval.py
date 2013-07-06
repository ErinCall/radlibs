from __future__ import unicode_literals

import json
from mock import patch
from flask import request
from radlibs.parser import parse, ParseError
from radlibs.web import app
from radlibs.web.json_endpoint import json_endpoint, error_response


@app.route('/demo_eval', methods=['POST'])
@json_endpoint
def demo_eval():
    try:
        rad = request.form['rad']
    except KeyError as e:
        return error_response("the 'rad' param is required")
    try:
        libs = request.form['libs']
        libs = json.loads(libs)
    except KeyError as e:
        return error_response("the 'libs' param is required")
    except ValueError as e:
        return error_response("'libs' param is not valid JSON: " + unicode(e))

    with patch('radlibs.parser.load_lib', lambda name: libs[name]):
        try:
            radlib = unicode(parse(rad))
        except KeyError as e:
            return error_response("No such Library '{0}'".format(e.message))
        except ParseError as e:
            return error_response(e.message)

    return {
        'status': 'ok',
        'radlib': radlib,
    }
