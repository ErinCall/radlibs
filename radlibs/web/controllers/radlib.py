from __future__ import unicode_literals

import re
import radlibs.lib
from flask import g, request, abort
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from radlibs import Client
from radlibs.web import app
from radlibs.table.association import Association, UserAssociation
from radlibs.table.radlib import Rad, Lib
from radlibs.web.json_endpoint import json_endpoint, error_response
from radlibs.parser import parse, ParseError


@app.route('/association/<int:association_id>/lib/new', methods=['POST'])
@json_endpoint
def create_lib(association_id):
    if not g.user:
        return error_response('login required')
    name = request.form['name']
    if not re.search('^[A-Z][a-z_]*$', name):
        return error_response("'{0}' is not a valid lib name".format(name))
    session = Client().session()
    try:
        find_association(association_id)
    except NoResultFound:
        return error_response('no such association')
    lib = Lib(association_id=association_id,
              name=name)
    session.add(lib)
    try:
        session.flush()
    except IntegrityError:
        return error_response('lib already exists')
    return {'status': 'ok', 'lib_id': lib.lib_id}


@app.route('/lib/$lib_id/rad/new', methods=['POST'], defaults={'lib_id': 0})
@app.route('/lib/<int:lib_id>/rad/new', methods=['POST'])
@json_endpoint
def new_rad(lib_id):
    if lib_id == 0:
        return error_response('lib_id is required')
    if not g.user:
        return error_response('login required')
    try:
        parse(request.form['rad'])
    except ParseError as e:
        return error_response('parse error: {0}'.format(e.message))
    session = Client().session()
    try:
        lib = find_lib(lib_id)
    except NoResultFound:
        return error_response('no such lib')
    rad = Rad(created_by=g.user.user_id,
              lib_id=lib_id,
              rad=request.form['rad'])
    session.add(rad)
    radlibs.lib.decache_lib(lib.name, lib.association_id)
    return {'status': 'ok'}


@app.route('/lib/rad/new', methods=['POST'])
@json_endpoint
def new_rad_by_name():
    if not g.user:
        return error_response('login required')
    try:
        parse(request.form['rad'])
    except ParseError as e:
        return error_response('parse error: {0}'.format(e.message))
    session = Client().session()
    lib_name = request.form['lib']
    association_id = request.form['association_id']
    try:
        find_association(association_id)
    except NoResultFound:
        return error_response('no such association')
    try:
        lib = session.query(Lib).\
            filter(Lib.name == lib_name).\
            filter(Lib.association_id == association_id).\
            one()
    except NoResultFound:
        return error_response("no such lib '{0}'".format(lib_name))
    rad = Rad(created_by=g.user.user_id,
              lib_id=lib.lib_id,
              rad=request.form['rad'])
    session.add(rad)
    radlibs.lib.decache_lib(lib.name, lib.association_id)
    return {'status': 'ok'}


@app.route('/lib/rad/$rad_id/edit', methods=['POST'], defaults={'rad_id': 0})
@app.route('/lib/rad/<int:rad_id>/edit', methods=['POST'])
@json_endpoint
def edit_rad(rad_id):
    if rad_id == 0:
        abort(404)
    if not g.user:
        return error_response('login required')
    try:
        parse(request.form['rad'])
    except ParseError as e:
        return error_response('parse error: {0}'.format(e.message))
    session = Client().session()
    try:
        (rad, lib) = session.query(Rad, Lib).\
            join(Lib).\
            join(Association).\
            join(UserAssociation).\
            filter(UserAssociation.user_id == g.user.user_id).\
            filter(Rad.rad_id == rad_id).\
            one()
    except NoResultFound:
        return error_response('no such rad')

    rad.rad = request.form['rad']
    session.add(rad)
    radlibs.lib.decache_lib(lib.name, lib.association_id)
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


def find_association(association_id):
    session = Client().session()
    return session.query(Association).\
        join(UserAssociation,
             UserAssociation.association_id == Association.association_id).\
        filter(Association.association_id == association_id).\
        filter(UserAssociation.user_id == g.user.user_id).\
        one()
