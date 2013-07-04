from __future__ import unicode_literals

import os
import json
import requests
from flask import request, g, redirect, make_response

from radlibs.web import app


@app.route('/token_url', methods=['POST'])
def token_url():
    token = request.form['token']
    api_params = {
        'token': token,
        'apiKey': os.environ['ENGAGE_API_KEY'],
        'format': 'json',
    }

    response = requests.get('https://rpxnow.com/api/v2/auth_info',
                            params=api_params)
    auth_info = json.loads(response.text)
    if 'profile' not in auth_info:
        return make_response('An error occurred interacting with your '
                             'identity provider. Since that does not '
                             'usually happen unless you are a radlibs '
                             'developer, here is the error in all its '
                             'terrible beauty: ' + response.text)
    identifier = auth_info['profile']['identifier']
    email = auth_info['profile'].get('email')

    redirect_uri = request.form.get('redirect_uri', '/')
    return redirect(redirect_uri)
