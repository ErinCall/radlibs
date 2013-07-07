from __future__ import unicode_literals

import json
from nose.tools import eq_, nottest
from tests import TestCase, logged_in
from radlibs.table.association import Association, UserAssociation
from radlibs.table.user import User
from radlibs.table.radlib import Rad, Lib
from radlibs import Client


class TestRadLib(TestCase):
    @logged_in
    def test_create_new_lib(self, user):
        session = Client().session()
        association_id = self.create_association(user)

        response = self.app.post(
            '/association/{0}/lib/new'.format(association_id),
            data={"name": "Rant"})
        lib = session.query(Lib).one()
        eq_(lib.name, 'Rant')

        eq_(response.status_code, 200, response.data)
        body = json.loads(response.data)
        eq_(body, {
            'status': 'ok',
            'lib_id': lib.lib_id,
            })

    @logged_in
    def test_create_new_lib__association_id_is_required(self, user):
        response = self.app.post(
            '/association/8/lib/new', data={"name": "Buffoonery"})
        eq_(response.status_code, 200, response.data)
        body = json.loads(response.data)
        eq_(body, {'status': 'error', 'error': 'no such association'})

    def test_create_new_lib__login_is_required(self):
        response = self.app.post(
            '/association/8/lib/new', data={"name": "Maleficence"})
        eq_(response.status_code, 200, response.data)
        body = json.loads(response.data)
        eq_(body, {'status': 'error', 'error': 'login required'})

    @logged_in
    def test_libcase_is_necessary(self, user):
        association_id = self.create_association(user)

        response = self.app.post(
            '/association/{0}/lib/new'.format(association_id),
            data={'name': 'not a valid name'})
        eq_(response.status_code, 200, response.data)
        body = json.loads(response.data)
        eq_(body, {
            'status': 'error',
            'error': "'not a valid name' is not a valid lib name",
            })

    @logged_in
    def test_view_lib(self, user):
        session = Client().session()
        association_id = self.create_association(user)

        lib = Lib(association_id=association_id, name='Rant')
        session.add(lib)
        session.flush()

        session.add(Rad(rad="My spoon is too big!",
                        lib_id=lib.lib_id,
                        created_by=user.user_id))
        session.add(Rad(rad="something something --Frank Herbert",
                        lib_id=lib.lib_id,
                        created_by=user.user_id))
        session.flush()

        response = self.app.get('/lib/{0}'.format(lib.lib_id))
        eq_(response.status_code, 200, response.data)
        assert "Rant" in response.data, "Didn't find lib name"
        assert "My spoon is too big!" in response.data, \
            "Didn't find first rant"
        assert "something something --Frank Herbert" in response.data, \
            "Didn't find second rant"

    @logged_in
    def test_view_lib_with_no_rads(self, user):
        session = Client().session()
        association_id = self.create_association(user)

        lib = Lib(association_id=association_id, name='Location')
        session.add(lib)
        session.flush()

        response = self.app.get('/lib/{0}'.format(lib.lib_id))
        eq_(response.status_code, 200, response.data)
        assert "Location" in response.data, "Didn't find lib name"

    def test_view_lib_requires_user(self):
        session = Client().session()
        association = Association(name='Partytown')
        session.add(association)
        session.flush()
        lib = Lib(name="Animal", association_id=association.association_id)
        session.add(lib)
        session.flush()

        response = self.app.get('/lib/{0}'.format(lib.lib_id))
        eq_(response.status_code, 404)

    @logged_in
    def test_view_lib_requires_correct_user(self, user):
        session = Client().session()
        other_user = User()
        association_id = self.create_association(other_user)
        lib = Lib(name="Song", association_id=association_id)
        session.add(lib)
        session.flush()

        response = self.app.get('/lib/{0}'.format(lib.lib_id))
        eq_(response.status_code, 404)

    def test_view_lib__nonexistent_lib_id(self):
        response = self.app.get('/lib/8')
        eq_(response.status_code, 404)

    @logged_in
    def test_add_new_rad(self, user):
        session = Client().session()
        association_id = self.create_association(user)
        lib = Lib(name="Artist", association_id=association_id)
        session.add(lib)
        session.flush()

        response = self.app.post('/lib/{0}/rad/new'.format(lib.lib_id),
                                 data={'rad': 'Shania Twain'})
        eq_(response.status_code, 200)

        rad = session.query(Rad).one()
        eq_(rad.created_by, user.user_id)
        eq_(rad.lib_id, lib.lib_id)
        eq_(rad.rad, 'Shania Twain')

        body = json.loads(response.data)
        eq_(body, {'status': 'ok'})

    @logged_in
    def test_add_new_rad__nonexistent_lib_id(self, user):
        response = self.app.post('/lib/8/rad/new',
                                 data={'rad': 'what is happening'})
        eq_(response.status_code, 200)
        body = json.loads(response.data)
        eq_(body, {'status': 'error', 'error': 'no such lib'})

    def test_add_new_rad__requires_user(self):
        session = Client().session()
        association = Association(name='Partytown')
        session.add(association)
        session.flush()
        lib = Lib(name="Animal", association_id=association.association_id)
        session.add(lib)
        session.flush()

        response = self.app.post('/lib/{0}/rad/new'.format(lib.lib_id),
                                 data={'rad': 'what is happening'})
        eq_(response.status_code, 200)
        body = json.loads(response.data)
        eq_(body, {
            'status': 'error',
            'error': 'login required'})

    @logged_in
    def test_add_new_rad__requires_correct_user(self, user):
        session = Client().session()
        other_user = User()
        association_id = self.create_association(other_user)
        lib = Lib(name="Song", association_id=association_id)
        session.add(lib)
        session.flush()

        response = self.app.post('/lib/{0}/rad/new'.format(lib.lib_id),
                                 data={'rad': '<Song_which_never_ends>'})
        eq_(response.status_code, 200)
        body = json.loads(response.data)
        eq_(body, {
            'status': 'error',
            'error': 'no such lib'})

    @nottest
    def create_association(self, user):
        session = Client().session()
        association = Association(name="Partytown")
        session.add(user)
        session.add(association)
        session.flush()

        user_association = UserAssociation(
            user_id=user.user_id,
            association_id=association.association_id)
        session.add(user_association)
        session.flush()

        return association.association_id
