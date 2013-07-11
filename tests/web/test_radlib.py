from __future__ import unicode_literals

import json
from nose.tools import eq_, nottest
from tests import TestCase, logged_in
from radlibs.table.association import Association, UserAssociation
from radlibs.table.user import User
from radlibs.table.radlib import Rad, Lib
from radlibs import Client
from nose.plugins.skip import SkipTest


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
    def test_create_new_lib__lib_already_exists(self, user):
        session = Client().session()
        association_id = self.create_association(user)
        lib = Lib(name="Rant", association_id=association_id)
        session.add(lib)
        session.flush()

        response = self.app.post(
            '/association/{0}/lib/new'.format(association_id),
            data={"name": "Rant"})

        eq_(response.status_code, 200, response.data)
        body = json.loads(response.data)
        eq_(body, {
            'status': 'error',
            'error': 'lib already exists'
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
    def test_new_lib__validate_name(self, user):
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

    @logged_in
    def test_add_new_rad_by_name(self, user):
        session = Client().session()
        association_id = self.create_association(user)
        lib = Lib(name="Song", association_id=association_id)
        session.add(lib)
        session.flush()

        response = self.app.post('/lib/rad/new', data={
            'association_id': association_id,
            'lib': 'Song',
            'rad': 'Stairway to <Location>',
        })
        eq_(response.status_code, 200)
        body = json.loads(response.data)
        eq_(body, {'status': 'ok'})

    @logged_in
    def test_new_rad_by_name__no_such_lib(self, user):
        association_id = self.create_association(user)

        response = self.app.post('/lib/rad/new', data={
            'association_id': association_id,
            'lib': 'Song',
            'rad': 'radar <Emotion>',
        })
        eq_(response.status_code, 200)
        body = json.loads(response.data)
        eq_(body, {
            "status": 'error',
            'error': "no such lib 'Song'"
            })

    @logged_in
    def test_new_rad_by_name__no_such_association_id(self, user):
        response = self.app.post('/lib/rad/new', data={
            'association_id': 8,
            'lib': 'Song',
            'rad': '<Color> Friday',
        })
        eq_(response.status_code, 200)
        body = json.loads(response.data)
        eq_(body, {
            "status": 'error',
            'error': "no such association",
            })

    def test_new_rad_by_name__requires_login(self):
        response = self.app.post('/lib/rad/new', data={
            'association_id': 8,
            'lib': 'Song',
            'rad': '<0-99> Problems',
        })
        eq_(response.status_code, 200)
        body = json.loads(response.data)
        eq_(body, {
            "status": 'error',
            'error': "login required",
            })

    @logged_in
    def test_new_rad_by_name__requires_correct_login(self, user):
        session = Client().session()
        other_user = User()
        association_id = self.create_association(other_user)
        lib = Lib(name="Song", association_id=association_id)
        session.add(lib)
        session.flush()

        response = self.app.post('/lib/rad/new', data={
            'association_id': association_id,
            'lib': 'Song',
            'rad': 'The sound of <Sound>',
        })
        eq_(response.status_code, 200)
        body = json.loads(response.data)
        eq_(body, {
            "status": 'error',
            'error': "no such association",
            })

    @logged_in
    def test_new_rad_by_name__missing_params(self, user):
        session = Client().session()
        association_id = self.create_association(user)
        lib = Lib(name="Song", association_id=association_id)
        session.add(lib)
        session.flush()

        response = self.app.post('/lib/rad/new', data={
            'lib': 'Song',
            'rad': 'Stairway to <Location>',
        })
        eq_(response.status_code, 200)
        body = json.loads(response.data)
        eq_(body, {
            'status': 'error',
            'error': "missing param 'association_id'"
            })

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
