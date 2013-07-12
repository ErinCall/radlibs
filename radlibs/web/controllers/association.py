from __future__ import unicode_literals

import re
from flask import render_template, g, url_for, redirect, request, abort
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from radlibs import Client
from radlibs.parser import parse, ParseError
from radlibs.web import app
from radlibs.table.association import (
    Association,
    UserAssociation,
    AssociationInvite)
from radlibs.table.user import User
from radlibs.table.radlib import Rad, Lib
from radlibs.mail import send_invitation_mail
from radlibs.web.json_endpoint import error_response, json_endpoint
from radlibs.web.breadcrumbs import breadcrumbs
from radlibs.date_utils import utcnow


@app.route('/associations')
def list_associations():
    if not g.user:
        abort(401)
    associations = Association.find_all_for_user(g.user)
    if associations:
        return render_template('list_associations.html.jinja',
                               associations=associations)
    else:
        return redirect(url_for('new_association'))


@app.route('/association/new')
def new_association():
    if not g.user:
        abort(401)
    return render_template('new_thing.html.jinja',
                           thing_name="Association",
                           breadcrumbs=breadcrumbs('New'))


@app.route('/association/new', methods=['POST'])
def create_association():
    if not g.user:
        abort(401)
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
    if not g.user:
        abort(401)
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
                            Rad.rad_id,
                            Rad.rad).\
        select_from(Lib).\
        outerjoin(Rad, Lib.lib_id == Rad.lib_id).\
        filter(Lib.association_id == association.association_id).\
        all()

    member_emails = session.query(User.email).\
        join(UserAssociation, UserAssociation.user_id == User.user_id).\
        filter(UserAssociation.association_id == association_id).\
        all()

    libs = {}
    for (lib_name, lib_id, rad_id, rad) in radlibs:
        if lib_name not in libs:
            libs[lib_name] = {'rads': []}
        libs[lib_name]['lib_id'] = lib_id
        if rad:
            libs[lib_name]['rads'].append({'rad_id': rad_id, 'rad': rad})
    return render_template('manage_association.html.jinja',
                           association=association,
                           libs=libs,
                           member_emails=[e[0] for e in member_emails],
                           breadcrumbs=breadcrumbs(association.name))


@app.route('/association/<int:association_id>/test_radlib', methods=['POST'])
@json_endpoint
def test_radlib(association_id):
    session = Client().session()
    if not g.user:
        return error_response('login required')
    try:
        association = association_for_logged_in_user(association_id)
    except NoResultFound:
        return error_response('no such association')

    g.association_id = association_id
    try:
        radlib = unicode(parse(request.form['rad']))
    except KeyError as e:
        return error_response("no such lib '{0}'".format(e.message))
    except ParseError as e:
        return error_response(e.message)
    return {'status': 'ok', 'radlib': radlib}


@app.route('/association/<int:association_id>/invite_user', methods=['POST'])
@json_endpoint
def invite_user(association_id):
    if not g.user:
        return error_response('login required')
    session = Client().session()
    email = request.form['email']
    if not re.search(r'@.*\.', email):
        return error_response("invalid email address '{0}'".format(email))
    try:
        association = association_for_logged_in_user(association_id)
    except NoResultFound:
        return error_response('no such association')
    try:
        user = session.query(User).\
            filter(User.email == email).\
            one()
    except NoResultFound:
        invite = AssociationInvite.generate(association_id, email)
        try:
            session.flush()
        except IntegrityError:
            return error_response('already invited')
        send_invitation_mail(
            email,
            g.user.email,
            association.name,
            url_for('accept_invitation', token=invite.token, _external=True))
        return {'status': 'ok', 'action': 'invited'}

    user_association = UserAssociation(
        user_id=user.user_id, association_id=association_id)
    session.add(user_association)
    try:
        session.flush()
    except IntegrityError:
        return error_response('already in association')
    return {'status': 'ok', 'action': 'added'}


@app.route('/accept_invitation/<token>/')
def accept_invitation(token):
    if not g.user:
        return render_template('invitation_registration.html.jinja')
    session = Client().session()
    try:
        invite = session.query(AssociationInvite).\
            filter(AssociationInvite.token == token).\
            one()
    except NoResultFound:
        abort(404)
    if invite.email != g.user.email:
        raise StandardError('Logged-in user had email {0} and a token for an '
                            'invite for {1}'.format(g.user.email, invite.email))
    session.add(UserAssociation(association_id=invite.association_id,
                                user_id=g.user.user_id))
    session.delete(invite)

    if g.user.email_verified_at is None:
        g.user.email_verified_at = utcnow()
        session.add(g.user)
    return redirect(url_for('manage_association',
                            association_id=invite.association_id))


def association_for_logged_in_user(association_id):
    return Client().session().query(Association).\
        join(UserAssociation,
             Association.association_id == UserAssociation.association_id).\
        filter(Association.association_id == association_id).\
        filter(UserAssociation.user_id == g.user.user_id).\
        one()
