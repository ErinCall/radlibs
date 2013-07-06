from __future__ import unicode_literals

from flask import render_template, g, url_for, redirect, request, abort
from sqlalchemy.orm.exc import NoResultFound
from radlibs import Client
from radlibs.parser import parse, ParseError
from radlibs.web import app
from radlibs.table.association import Association, UserAssociation
from radlibs.table.radlib import Rad, Lib
from radlibs.web.json_endpoint import error_response, json_endpoint


@app.route('/associations')
def list_associations():
    associations = Association.find_all_for_user(g.user)
    if associations:
        return render_template('list_associations.html.jinja',
                               associations=associations)
    else:
        return redirect(url_for('new_association'))


@app.route('/association/new')
def new_association():
    return render_template('new_thing.html.jinja', thing_name="Association")


@app.route('/association/new', methods=['POST'])
def create_association():
    name = request.form['name']
    session = Client().session()
    association = Association(name=name)
    session.add(association)
    session.flush()

    user_association = UserAssociation(
        user_id=g.user.user_id,
        association_id=association.association_id)
    session.add(user_association)

    return redirect(url_for('manage_association',
                            association_id=association.association_id))


@app.route('/association/<int:association_id>')
def manage_association(association_id):
    session = Client().session()
    try:
        association = session.query(Association).\
            join(UserAssociation,
                 UserAssociation.association_id == Association.association_id).\
            filter(Association.association_id == association_id).\
            filter(UserAssociation.user_id == g.user.user_id).\
            one()
    except NoResultFound:
        abort(404)
    radlibs = session.query(Lib.name,
                            Lib.lib_id,
                            Rad.rad).\
        select_from(Lib).\
        outerjoin(Rad, Lib.lib_id == Rad.lib_id).\
        filter(Lib.association_id == association.association_id).\
        all()

    libs = {}
    for (lib_name, lib_id, rad) in radlibs:
        if lib_name not in libs:
            libs[lib_name] = {'rads': []}
        libs[lib_name]['lib_id'] = lib_id
        if rad:
            libs[lib_name]['rads'].append(rad)
    return render_template('manage_association.html.jinja',
                           association=association,
                           libs=libs)


@app.route('/association/<int:association_id>/test_radlib', methods=['POST'])
@json_endpoint
def test_radlib(association_id):
    session = Client().session()
    if not g.user:
        return error_response('login required')
    associations = session.query(Association).\
        join(UserAssociation,
             Association.association_id == UserAssociation.association_id).\
        filter(Association.association_id == association_id).\
        filter(UserAssociation.user_id == g.user.user_id).\
        count()

    if not associations:
        return error_response('no such association')

    g.association_id = association_id
    try:
        radlib = unicode(parse(request.form['rad']))
    except KeyError as e:
        return error_response("no such lib '{0}'".format(e.message))
    except ParseError as e:
        return error_response(e.message)
    return {'status': 'ok', 'radlib': radlib}