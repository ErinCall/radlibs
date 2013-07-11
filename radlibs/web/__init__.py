from __future__ import unicode_literals

import sha
import os
import logging
import datetime
import redis
from logging.handlers import SMTPHandler
from werkzeug.contrib.cache import RedisCache, SimpleCache
from flask import Flask, render_template, g, session, request
from flask.ext.assets import Environment, Bundle
from flask_s3 import FlaskS3
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

if 'REDISTOGO_URL' in os.environ:
    redis_client = redis.from_url(os.environ['REDISTOGO_URL'])
    app.cache = RedisCache(redis_client)
else:
    app.cache = SimpleCache()

app.config['S3_BUCKET_NAME'] = 'radlibs-assets'
app.config['S3_USE_CACHE_CONTROL'] = False
app.config['S3_CDN_DOMAIN'] = 'd2hwb9ozcl9dk9.cloudfront.net'
app.config['FLASK_ASSETS_USE_S3'] = True
app.config['USE_S3_DEBUG'] = True
if os.getenv('ASSETS_DEBUG'):
    app.config['ASSETS_DEBUG'] = True
    app.config['FLASK_ASSETS_USE_S3'] = False
FlaskS3(app)
assets = Environment(app)
js = Bundle('js/jquery.min.js',
            'js/bootstrap.min.js',
            'js/underscore-min.js',
            'js/radlibs.js',
            'js/janrain.js',
            'js/live_demo.js',
            'js/invitation_registration.js',
            'js/edit_association.js',
            filters='jsmin',
            output='gen/packed.%(version)s.js')
assets.register('js_all', js)
css = Bundle("css/bootstrap.min.css",
             "css/bootstrap-responsive.min.css",
             "css/layout.css",
             filters='cssmin',
             output='gen/packed.%(version)s.css')
assets.register('css_all', css)


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
            client_time = datetime.datetime.strptime(time, '%Y%m%dT%H:%M:%S')
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
        for key in sorted(params.keys()):
            plaintext = plaintext + "{0}: {1}\n".format(key, params[key][0])
        plaintext = plaintext + request.path + "\n"
        plaintext = plaintext + user.api_key
        calculated_signature = sha.sha(plaintext.encode('utf-8')).hexdigest()
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


@app.route('/api/')
def api():
    return render_template('api.html.jinja')


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
import radlibs.web.controllers.profile


@app.context_processor
def build_menu():
    if g.user:
        return {'menu': [
            ('api', 'The API'),
            ('language', 'The Language'),
            ('list_associations', 'Associations'),
            ('profile', 'Profile'),
        ]}
    else:
        return {'menu': [
            ('live_demo', 'Try It Live'),
            ('language', 'The Language'),
        ]}


@app.context_processor
def breadcrumbs():
    return {'breadcrumbs': []}
