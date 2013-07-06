from __future__ import unicode_literals

import os
from flask import Flask, render_template, g, session
from radlibs import Client
from radlibs.table.user import User

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
app = Flask(__name__, static_folder=os.path.join(PROJECT_ROOT, 'static'),
            static_url_path='/static')
app.secret_key = os.environ.get('SECRET_KEY')
if 'SERVER_NAME' in os.environ:
    app.config['SERVER_NAME'] = os.environ['SERVER_NAME']


@app.before_request
def before_request():
    if not hasattr(g, 'user'):
        g.user = None
    if 'user' in session:
        user = Client().session().query(User).\
            filter(User.email == session['user']['email']).\
            one()
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
