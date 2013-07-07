from __future__ import unicode_literals

import sha
import os
import logging
import datetime
from logging.handlers import SMTPHandler
from flask import Flask, render_template, g, session, request
from sqlalchemy.orm.exc import NoResultFound
from radlibs import Client
from radlibs.table.user import User

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
app = Flask(__name__, static_folder=os.path.join(PROJECT_ROOT, 'static'),
            static_url_path='/static')
app.secret_key = os.environ.get('SECRET_KEY')
if 'SERVER_NAME' in os.environ:
    app.config['SERVER_NAME'] = os.environ['SERVER_NAME']

if 'SENDGRID_PASSWORD' in os.environ and not app.debug:
    mail_handler = SMTPHandler('smtp.sendgrid.net',
                               'errors@radlibs.info',
                               ['andrew.lorente@gmail.com'],
                               'Radlib error',
                               (os.environ['SENDGRID_USERNAME'], os.environ['SENDGRID_PASSWORD']))
    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(logging.Formatter('''
Message type:       %(levelname)s
Location:           %(pathname)s:%(lineno)d
Module:             %(module)s
Function:           %(funcName)s
Time:               %(asctime)s

Message:

%(message)s
'''))
    app.logger.addHandler(mail_handler)


@app.before_request
def before_request():
    if not hasattr(g, 'user'):
        g.user = None
    if 'user' in session:
        user = Client().session().query(User).\
            filter(User.email == session['user']['email']).\
            one()
        g.user = user
    elif all(map(lambda x: x in request.form,
                 ['signature', 'user_id', 'time'])):
        params = dict(request.form)
        signature = params.pop('signature')[0]
        user_id = params.pop('user_id')[0]
        time = params.pop('time')[0]
        try:
            client_time = datetime.datetime.strptime(time, '%Y%m%d %H:%M:%S')
        except ValueError:
            return
        current_time = datetime.datetime.utcnow()
        if abs(client_time - current_time) > datetime.timedelta(0, 5*60, 0):
            return
        try:
            user = Client().session().query(User).\
                filter(User.user_id == user_id).\
                one()
        except NoResultFound:
            return
        if not user.api_key:
            return
        plaintext = time + "\n"
        for (key, value) in params.iteritems():
            plaintext = plaintext + "{0}: {1}\n".format(key, value[0])
        plaintext = plaintext + request.path + "\n"
        plaintext = plaintext + user.api_key
        calculated_signature = sha.sha(plaintext).hexdigest()
        if calculated_signature == signature:
            g.user = user

@app.after_request
def after_request(response):
    Client().session().commit()
    return response


@app.route('/')
def index():
    return render_template('index.html.jinja')


@app.route('/live_demo/')
def live_demo():
    return render_template('live_demo.html.jinja')


@app.route('/language/')
def language():
    return render_template('language.html.jinja')


@app.route('/privacy_policy')
def privacy_policy():
    return render_template('privacy_policy.html.jinja')

import radlibs.web.controllers.demo_eval
import radlibs.web.controllers.login
import radlibs.web.controllers.association
import radlibs.web.controllers.radlib


@app.context_processor
def build_menu():
    if g.user:
        return {'menu': [
            ('language', 'The Language'),
            ('list_associations', 'Associations'),
        ]}
    else:
        return {'menu': [
            ('live_demo', 'Try It Live'),
            ('language', 'The Language'),
        ]}


@app.context_processor
def breadcrumbs():
    return {'breadcrumbs': []}
