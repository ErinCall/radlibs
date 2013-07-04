from __future__ import unicode_literals

import json
from mock import patch
from flask import request, make_response
from radlibs.web import app
from radlibs.expand import expand


@app.route('/demo_eval', methods=['POST'])
def demo_eval():
    rad = request.form.get('rad')
    libs = json.loads(request.form.get('libs'))
    print libs

    #TODO: exception handler here
    def load_lib(lib_name):
        return libs[lib_name]

    with patch('radlibs.parser.load_lib', load_lib):
        radlib = expand(rad)

    return make_response(json.dumps({
        'status': 'ok',
        'radlib': radlib,
    }))
