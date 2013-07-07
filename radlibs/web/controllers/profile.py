from __future__ import unicode_literals

from flask import render_template, g, abort, url_for, redirect
from radlibs.web import app


@app.route('/profile')
def profile():
    if not g.user:
        abort(401)
    return render_template('profile.html.jinja')


@app.route('/profile/get_api_key', methods=['POST'])
def get_api_key():
    if not g.user:
        abort(401)
    g.user.generate_api_key()
    return redirect(url_for('profile'))
