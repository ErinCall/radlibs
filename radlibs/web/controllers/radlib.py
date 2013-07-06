from __future__ import unicode_literals

from flask import render_template, g, url_for, redirect, request, abort
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from parsimonious.exceptions import IncompleteParseError
from radlibs import Client
from radlibs.web import app
from radlibs.table.association import Association, UserAssociation
from radlibs.table.radlib import Rad, Lib
from radlibs.parser import parse
from radlibs.web.json_endpoint import json_endpoint, error_response


@app.route('/lib/new/<int:association_id>')
def new_lib(association_id):
    return render_template('new_thing.html.jinja',
                           thing_name='Lib',
                           hidden_values={'association_id': association_id})


@app.route('/lib/new/<int:association_id>', methods=['POST'])
def create_lib(association_id):
    if not g.user:
        abort(401)
    name = request.form['name']
    try:
        parse('<{0}>'.format(name))
    except IncompleteParseError:
        return render_template(
            'new_thing.html.jinja', thing_name='Lib',
            hidden_values={'association_id': association_id},
            error="'{0}' is not a valid lib name. Lib names must be a single "
            "letter followed by only letters and underscores.".format(name),
        )
    session = Client().session()
    associations = session.query(Association).\
        join(UserAssociation, UserAssociation.association_id == association_id).\
        filter(Association.association_id == association_id).\
        filter(UserAssociation.user_id == g.user.user_id).\
        all()
    if not associations:
        abort(404)
    lib = Lib(association_id=association_id,
              name=name)
    session.add(lib)
    session.flush()
    return redirect(url_for('view_lib', lib_id=lib.lib_id))


@app.route('/lib/<int:lib_id>')
def view_lib(lib_id):
    if not g.user:
        abort(404)
    session = Client().session()
    try:
        lib = find_lib(lib_id)
    except NoResultFound:
        abort(404)
    rads = session.query(Rad).filter(Rad.lib_id == lib_id).all()
    return render_template('view_lib.html.jinja', lib=lib, rads=rads)


@app.route('/lib/<int:lib_id>/rad/new', methods=['POST'])
@json_endpoint
def new_rad(lib_id):
    if not g.user:
        return error_response('login required')
    session = Client().session()
    try:
        find_lib(lib_id)
    except NoResultFound:
        return error_response('no such lib')
    rad = Rad(created_by=g.user.user_id,
              lib_id=lib_id,
              rad=request.form['rad'])
    session.add(rad)
    return {'status': 'ok'}


def find_lib(lib_id):
    return Client().session().query(Lib).\
            join(Association,
                 Association.association_id == Lib.association_id).\
            join(UserAssociation,
                 UserAssociation.association_id == Association.association_id).\
            filter(UserAssociation.user_id == g.user.user_id).\
            filter(Lib.lib_id == lib_id).\
            one()