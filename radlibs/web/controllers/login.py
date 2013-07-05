from __future__ import unicode_literals

import os
import json
import urlparse
import requests
from flask import request,\
    redirect,\
    make_response,\
    session,\
    url_for,\
    render_template
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError

from radlibs import Client
from radlibs.web import app
from radlibs.table.user import User


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

    db_session = Client().session()
    try:
        print repr(identifier)
        user = db_session.query(User).\
            filter(User.identifier == identifier).\
            one()
    except NoResultFound:
        if email:
            existing_users = db_session.query(User).\
                filter(User.email == email).\
                all()
            if existing_users:
                provider = provider_for_identifier(
                    existing_users[0].identifier)
                return render_template(
                    'identifier_mismatch.html.jinja',
                    existing_provider=provider)
            user = User(email=email, identifier=identifier)
            db_session.add(user)
            session['user'] = {'identifier': identifier, 'email': email}
        else:
            session['partial_user'] = {'identifier': identifier}
            return redirect(url_for('show_registration',
                                    redirect_uri=redirect_uri))

    return redirect(redirect_uri)


@app.route('/complete_registration', methods=['GET'])
def show_registration():
    redirect_uri = request.args.get('redirect_uri', '/')
    return render_template('complete_registration.html.jinja',
                           redirect_uri=redirect_uri)


@app.route('/complete_registration', methods=['POST'])
def register():
    user = User(
        email=request.form['email'],
        identifier=session['partial_user']['identifier'])
    db_session = Client().session()
    db_session.add(user)
    session['user'] = {'email': user.email, 'identifier': user.identifier}
    return redirect(request.form['redirect_uri'])

def provider_for_identifier(identifier):
    parsed = urlparse.urlparse(identifier)
    return {
        'www.facebook.com': 'Facebook',
        'www.live.coom': 'Live',
        'www.twitter.com': 'Twitter',
        'www.amazon.com': 'Amazon',
        'www.google.com': 'Google',
    }.get(parsed.netloc, parsed.netloc)
