from __future__ import unicode_literals

import json
from mock import patch
from flask import request
from parsimonious.exceptions import IncompleteParseError
from radlibs.parser import parse
from radlibs.web import app
from radlibs.web.json_endpoint import json_endpoint


@app.route('/demo_eval', methods=['POST'])
@json_endpoint
def demo_eval():
    try:
        rad = request.form['rad']
    except KeyError as e:
        return _error("the 'rad' param is required")
    try:
        libs = request.form['libs']
        libs = json.loads(libs)
    except KeyError as e:
        return _error("the 'libs' param is required")
    except ValueError as e:
        return _error("'libs' param is not valid JSON: " + unicode(e))

    with patch('radlibs.parser.load_lib', lambda name: libs[name]):
        try:
            radlib = unicode(parse(rad))
        except KeyError as e:
            return _error("No such Library '{0}'".format(e.message))
        except IncompleteParseError as e:
            return _error(unicode(e))

    return {
        'status': 'ok',
        'radlib': radlib,
    }


def _error(error_string):
    return {
        'status': 'error',
        'error': error_string,
    }
