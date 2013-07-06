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
    render_template,\
    abort
from sqlalchemy.orm.exc import NoResultFound

from radlibs import Client
from radlibs.web import app
from radlibs.mail import send_verification_mail
from radlibs.table.user import User, EmailVerificationToken
from radlibs.date_utils import utcnow


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
            user = User(email=email,
                        identifier=identifier,
                        email_verified_at=utcnow())
            db_session.add(user)
        else:
            session['partial_user'] = {'identifier': identifier}
            return redirect(url_for('show_registration',
                                    redirect_uri=redirect_uri))

    session['user'] = {'identifier': identifier, 'email': email}
    return redirect(redirect_uri)


@app.route('/complete_registration', methods=['GET'])
def show_registration():
    redirect_uri = request.args.get('redirect_uri', '/')
    return render_template('complete_registration.html.jinja',
                           redirect_uri=redirect_uri)


@app.route('/complete_registration', methods=['POST'])
def register():
    db_session = Client().session()
    user = User(
        email=request.form['email'],
        identifier=session['partial_user']['identifier'])
    db_session.add(user)
    db_session.flush()
    token = EmailVerificationToken.generate(user)
    send_verification_mail(
        user, url_for('verify_email', token=token.token, _external=True))
    session['user'] = {'email': user.email, 'identifier': user.identifier}
    return redirect(request.form['redirect_uri'])


@app.route('/verify_email/<token>')
def verify_email(token):
    db_session = Client().session()
    try:
        verification_token = db_session.query(EmailVerificationToken).\
            filter(EmailVerificationToken.token == token).\
            one()

        user = db_session.query(User).\
            filter(User.user_id == verification_token.user_id).\
            one()
    except NoResultFound:
        abort(404)
    user.email_verified_at = utcnow()
    db_session.add(user)
    db_session.delete(verification_token)

    return render_template('verification_complete.html.jinja')


@app.route('/logout')
def logout():
    if 'user' in session:
        del(session['user'])
    return redirect(url_for('index'))


def provider_for_identifier(identifier):
    parsed = urlparse.urlparse(identifier)
    return {
        'www.facebook.com': 'Facebook',
        'www.live.com': 'Live',
        'www.twitter.com': 'Twitter',
        'www.amazon.com': 'Amazon',
        'www.google.com': 'Google',
    }.get(parsed.netloc, parsed.netloc)
