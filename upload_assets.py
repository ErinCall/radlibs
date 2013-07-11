#!/usr/bin/env python

from radlibs.web import app, js, css
import flask_s3

js.urls()
css.urls()
flask_s3.create_all(app)
