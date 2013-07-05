from __future__ import unicode_literals

from flask import render_template, g, url_for, redirect, request, abort
from sqlalchemy.orm.exc import NoResultFound
from radlibs import Client
from radlibs.web import app
from radlibs.table.association import Association, UserAssociation


@app.route('/list_associations')
def list_associations():
    associations = Association.find_all_for_user(g.user)
    if associations:
        return render_template('list_associations.html.jinja',
                               associations=associations)
    else:
        return redirect(url_for('new_association'))


@app.route('/new_association')
def new_association():
    return render_template('new_association.html.jinja')


@app.route('/new_association', methods=['POST'])
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


@app.route('/association/<association_id>')
def manage_association(association_id):
    try:
        association = Client().session().query(Association).\
            join(UserAssociation,
                 UserAssociation.association_id == Association.association_id).\
            filter(Association.association_id == association_id).\
            filter(UserAssociation.user_id == g.user.user_id).\
            one()
    except NoResultFound:
        abort(404)
    return render_template('manage_association.html.jinja',
                           association=association)


@app.route('/association/<association_id>', methods=['POST'])
def update_association(association_id):
    pass
