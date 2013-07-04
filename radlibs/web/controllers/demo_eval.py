from __future__ import unicode_literals

import json
from mock import patch
from flask import request, make_response
from parsimonious.exceptions import IncompleteParseError
from radlibs.web import app
from radlibs.expand import expand


@app.route('/demo_eval', methods=['POST'])
def demo_eval():
    try:
        rad = request.form['rad']
    except KeyError as e:
        return make_response(json.dumps({
            'status': 'error',
            'error': "the 'rad' param is required",
        }))
    try:
        libs = request.form['libs']
        libs = json.loads(libs)
    except KeyError as e:
        return make_response(json.dumps({
            'status': 'error',
            'error': "the 'libs' param is required",
        }))
    except ValueError as e:
        return make_response(json.dumps({
            'status': 'error',
            'error': "'libs' param is not valid JSON: " + str(e),
        }))

    with patch('radlibs.parser.load_lib', lambda name: libs[name]):
        try:
            radlib = expand(rad)
        except KeyError as e:
            return make_response(json.dumps({
                'status': 'error',
                'error': "No such Library '{0}'".format(e.message),
            }))
        except IncompleteParseError as e:
            return make_response(json.dumps({
                'status': 'error',
                'error': str(e),
            }))

    return make_response(json.dumps({
        'status': 'ok',
        'radlib': radlib,
    }))
