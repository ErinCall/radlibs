from __future__ import unicode_literals

import os
from flask import Flask, render_template, g, session, request
from radlibs import Client

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
app = Flask(__name__, static_folder=os.path.join(PROJECT_ROOT, 'static'),
            static_url_path='/static')
app.secret_key = os.environ['SECRET_KEY']


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

import radlibs.web.controllers.demo_eval
