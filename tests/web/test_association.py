from __future__ import unicode_literals

import json
from mock import patch
from nose.tools import eq_
from tests import TestCase, logged_in
from radlibs.table.association import (
    Association,
    UserAssociation,
    AssociationInvite)
from radlibs.table.user import User
from radlibs.table.radlib import Rad, Lib
from radlibs import Client
from radlibs.date_utils import utcnow

from nose.plugins.skip import SkipTest


class TestAssociation(TestCase):
    @logged_in
    def test_association_list_redirects_to_create_if_user_has_none(self, user):
        response = self.app.get('/associations')
        eq_(response.status_code, 302, response.data)

    def test_association_list_requires_login(self):
        response = self.app.get('/associations')
        eq_(response.status_code, 401, response.data)

    @logged_in
    def test_association_list_lists_associations(self, user):
        session = Client().session()
        watercooler = Association(name='watercooler')
        codescouts = Association(name='codescouts')
        session.add(watercooler)
        session.add(codescouts)
        session.flush()

        session.add(UserAssociation(
            association_id=watercooler.association_id, user_id=user.user_id))
        session.add(UserAssociation(
            association_id=codescouts.association_id, user_id=user.user_id))
        response = self.app.get('/associations')

        eq_(response.status_code, 200, response.data)
        assert 'watercooler' in response.data, response.data
        assert 'codescouts' in response.data, response.data
        assert 'create a new association' in response.data, response.data

    @logged_in
    def test_view_new_association_page(self, user):
        response = self.app.get('/association/new')
        assert 'Create New Association' in response.data, \
            "Didn't see new-association message"

    @logged_in
    def test_create_new_association(self, user):
        session = Client().session()
        response = self.app.post('/association/new',
                                 data={'name': 'codescouts'})
        association = session.query(Association).one()
        user_association = session.query(UserAssociation).one()
        eq_(user_association.association_id, association.association_id)
        eq_(user_association.user_id, user.user_id)
        eq_(association.name, 'codescouts')
        eq_(response.status_code, 302, response.data)
        eq_(response.headers['Location'],
            'http://localhost/association/{0}'.format(
                association.association_id))

    @logged_in
    def test_users_can_only_manage_their_own_associations(self, user):
        session = Client().session()
        other_user = User(email='imogenheap@umg.com',
                          identifier='facebook.com/imogenheap')
        session.add(other_user)
        association = Association(name="lalala")
        session.add(association)
        session.flush()
        user_association = UserAssociation(
            user_id=other_user.user_id,
            association_id=association.association_id)
        session.add(user_association)
        session.flush()

        response = self.app.get('/association/{0}'.format(
            association.association_id))
        eq_(response.status_code, 404, response.data)

    @logged_in
    def test_see_libs_and_rads_in_an_association(self, user):
        session = Client().session()
        watercooler = Association(name='watercooler')
        rtk = Association(name='rtk')
        session.add(watercooler)
        session.add(rtk)

        session.flush()

        session.add(UserAssociation(
            association_id=rtk.association_id, user_id=user.user_id))
        session.add(UserAssociation(
            association_id=watercooler.association_id, user_id=user.user_id))

        session.flush()

        rant = Lib(name='Rant', association_id=rtk.association_id)
        food = Lib(name="Food", association_id=watercooler.association_id)
        animal = Lib(name="Animal", association_id=watercooler.association_id)
        session.add(rant)
        session.add(food)
        session.add(animal)
        session.flush()

        chili = Rad(
            rad="Chili con carne",
            lib_id=food.lib_id,
            created_by=user.user_id)
        session.add(chili)
        eggs = Rad(
            rad="<Animal> eggs",
            lib_id=food.lib_id,
            created_by=user.user_id)
        session.add(eggs)
        buzzhawk = Rad(
            rad="Buzzhawk",
            lib_id=animal.lib_id,
            created_by=user.user_id)
        session.add(buzzhawk)

        response = self.app.get('/association/{0}'.format(
            watercooler.association_id))

        eq_(response.status_code, 200, response.data)
        assert 'Food' in response.data, "didn't see food"
        assert 'Animal' in response.data, "didn't see animal"
        assert "Rant" not in response.data, "saw some other association's lib"

        assert 'Chili con carne' in response.data, "didn't see Chili"
        assert '&lt;Animal&gt; eggs' in response.data, "didn't see eggs"
        assert 'Buzzhawk' in response.data, "didn't see buzzhawk"

        assert 'data-rad_id="{0}"'.format(chili.rad_id) in response.data, \
            "didn't see chili.rad_id"
        assert 'data-rad_id="{0}"'.format(eggs.rad_id) in response.data, \
            "didn't see eggs.rad_id"
        assert 'data-rad_id="{0}"'.format(buzzhawk.rad_id) in response.data, \
            "didn't see buzzhawk.rad_id"

    @logged_in
    def test_see_libs_with_no_associated_rad(self, user):
        session = Client().session()
        watercooler = Association(name='watercooler')
        session.add(watercooler)
        session.flush()

        user_association = UserAssociation(
            association_id=watercooler.association_id,
            user_id=user.user_id)
        session.add(user_association)

        rant = Lib(name='Rant', association_id=watercooler.association_id)
        session.add(rant),
        session.flush()

        url = '/association/{0}'.format(watercooler.association_id)
        response = self.app.get(url)

        eq_(response.status_code, 200, response.data)

        assert 'Rant' in response.data, "didn't see rant"

    @logged_in
    def test_test_radlib(self, user):
        association = Association(name="codescouts")
        session = Client().session()
        session.add(association)
        session.flush()
        user_association = UserAssociation(
            user_id=user.user_id, association_id=association.association_id)
        session.add(user_association)

        animal = Lib(name="Animal", association_id=association.association_id)
        food = Lib(name="Food", association_id=association.association_id)
        session.add(animal)
        session.add(food)
        session.flush()

        session.add(Rad(lib_id=animal.lib_id,
                        created_by=user.user_id,
                        rad="Ostrich"))
        session.add(Rad(lib_id=food.lib_id,
                        created_by=user.user_id,
                        rad="<Animal> eggs"))
        session.flush()

        response = self.app.post(
            '/association/{0}/test_radlib'.format(association.association_id),
            data={'rad': 'I ate some <Food>'})
        eq_(response.status_code, 200)
        body = json.loads(response.data)
        eq_(body, {
            'status': 'ok',
            'radlib': 'I ate some Ostrich eggs'})

    def test_test_radlib_requires_login(self):
        session = Client().session()
        association = Association(name="somebody's private stuff")
        session.add(association)
        session.flush()
        response = self.app.post(
            '/association/{0}/test_radlib'.format(association.association_id),
            data={'rad': 'I ate some <Food>'})
        eq_(response.status_code, 200)
        body = json.loads(response.data)
        eq_(body, {
            'status': 'error',
            'error': 'login required'})

    @logged_in
    def test_test_radlib_requires_correct_user(self, user):
        session = Client().session()
        other_user = User()
        association = Association(name="my stuff")
        session.add(other_user)
        session.add(association)
        session.flush()
        session.add(UserAssociation(user_id=other_user.user_id,
                                    association_id=association.association_id))

        response = self.app.post(
            '/association/{0}/test_radlib'.format(association.association_id),
            data={'rad': 'I ate some <Food>'})
        eq_(response.status_code, 200)
        body = json.loads(response.data)
        eq_(body, {
            'status': 'error',
            'error': 'no such association'})

    @logged_in
    def test_test_radlib_with_unknown_lib(self, user):
        session = Client().session()
        association = Association(name="pdx python")
        session.add(association)
        session.flush()
        session.add(UserAssociation(user_id=user.user_id,
                                    association_id=association.association_id))

        response = self.app.post(
            '/association/{0}/test_radlib'.format(association.association_id),
            data={'rad': 'I ate some <Food>'})
        eq_(response.status_code, 200)
        body = json.loads(response.data)
        eq_(body, {
            'status': 'error',
            'error': "no such lib 'Food'"})

    @logged_in
    def test_test_radlib_with_syntactically_invalid_rad(self, user):
        session = Client().session()
        association = Association(name="pdx python")
        session.add(association)
        session.flush()
        session.add(UserAssociation(user_id=user.user_id,
                                    association_id=association.association_id))

        response = self.app.post(
            '/association/{0}/test_radlib'.format(association.association_id),
            data={'rad': 'I ate some Food>'})
        eq_(response.status_code, 200)
        body = json.loads(response.data)
        eq_(body, {
            'status': 'error',
            'error': "Unexpected token '>' at line 1 character 16 of "
            "'I ate some Food>'"})

    @logged_in
    def test_add_existing_user_to_association(self, user):
        session = Client().session()

        association = Association(name='prancing ponies')
        session.add(association)
        session.flush()
        session.add(UserAssociation(user_id=user.user_id,
                                    association_id=association.association_id))
        other_user = User(email_verified_at=utcnow(), email='friendly@ema.il')
        session.add(other_user)
        session.flush()

        response = self.app.post(
            '/association/{0}/invite_user'.format(association.association_id),
            data={'email': 'friendly@ema.il'})
        eq_(response.status_code, 200, response.data)
        body = json.loads(response.data)
        eq_(body, {'status': 'ok', 'action': 'added'})

        user_associations = session.query(
            UserAssociation.user_id, UserAssociation.association_id).\
            all()
        eq_(user_associations, [
            (user.user_id, association.association_id),
            (other_user.user_id, association.association_id),
            ])

    def test_add_user_to_association_requires_login(self):
        session = Client().session()

        association = Association(name='prancing ponies')
        session.add(association)
        session.flush()

        response = self.app.post(
            '/association/{0}/invite_user'.format(association.association_id),
            data={'email': 'myself@ema.il'})
        eq_(response.status_code, 200)

        body = json.loads(response.data)
        eq_(body, {
            'status': 'error',
            'error': 'login required'})

    @logged_in
    def test_add_user_to_association_requires_correct_login(self, user):
        session = Client().session()

        association = Association(name='prancing ponies')
        session.add(association)
        session.flush()

        response = self.app.post(
            '/association/{0}/invite_user'.format(association.association_id),
            data={'email': 'myself@ema.il'})
        eq_(response.status_code, 200)

        body = json.loads(response.data)
        eq_(body, {
            'status': 'error',
            'error': 'no such association'})

    @logged_in
    @patch('radlibs.web.controllers.association.send_invitation_mail')
    def test_invite_new_user_to_association(self, user, send_invitation_mail):
        user.email = "inviting@ema.il"
        session = Client().session()

        association = Association(name='prancing ponies')
        session.add(association)
        session.flush()
        session.add(UserAssociation(user_id=user.user_id,
                                    association_id=association.association_id))
        session.flush()

        response = self.app.post(
            '/association/{0}/invite_user'.format(association.association_id),
            data={'email': 'fng@ema.il'})
        eq_(response.status_code, 200, response.data)
        body = json.loads(response.data)
        eq_(body, {'status': 'ok', 'action': 'invited'})

        invite = session.query(AssociationInvite).one()
        eq_(invite.email, 'fng@ema.il')
        eq_(invite.association_id, association.association_id)

        send_invitation_mail.assert_called_once_with(
            'fng@ema.il',
            'inviting@ema.il',
            'prancing ponies',
            'http://localhost/accept_invitation/{0}/'.format(invite.token))

    @logged_in
    def test_invite__user_has_been_invited_to_another_association(self, user):
        session = Client().session()

        watercooler = Association(name='watercooler')
        pdxpython = Association(name='pdxpython')
        session.add(watercooler)
        session.add(pdxpython)
        session.flush()
        session.add(UserAssociation(user_id=user.user_id,
                                    association_id=watercooler.association_id))
        session.flush()

        AssociationInvite.generate(pdxpython.association_id, 'fng@ema.il')

        response = self.app.post(
            '/association/{0}/invite_user'.format(watercooler.association_id),
            data={'email': 'fng@ema.il'})
        eq_(response.status_code, 200, response.data)
        body = json.loads(response.data)
        eq_(body, {'status': 'ok', 'action': 'invited'})

    @logged_in
    def test_invite_a_user_who_has_been_invited_to_that_association(self, user):
        session = Client().session()

        watercooler = Association(name='watercooler')
        session.add(watercooler)
        session.flush()
        session.add(UserAssociation(user_id=user.user_id,
                                    association_id=watercooler.association_id))
        session.flush()

        AssociationInvite.generate(watercooler.association_id, 'fng@ema.il')

        response = self.app.post(
            '/association/{0}/invite_user'.format(watercooler.association_id),
            data={'email': 'fng@ema.il'})
        eq_(response.status_code, 200, response.data)
        body = json.loads(response.data)
        eq_(body, {'status': 'error', 'error': 'already invited'})

    @logged_in
    def test_invite__user_is_already_in_the_association(self, user):
        session = Client().session()

        watercooler = Association(name='watercooler')
        session.add(watercooler)
        session.flush()
        session.add(UserAssociation(user_id=user.user_id,
                                    association_id=watercooler.association_id))
        session.flush()

        response = self.app.post(
            '/association/{0}/invite_user'.format(watercooler.association_id),
            data={'email': user.email})
        eq_(response.status_code, 200)
        body = json.loads(response.data)
        eq_(body, {'status': 'error',
                   'error': 'already in association'})

    @logged_in
    def test_invite__invalid_email_address(self, user):
        session = Client().session()

        watercooler = Association(name='watercooler')
        session.add(watercooler)
        session.flush()
        session.add(UserAssociation(user_id=user.user_id,
                                    association_id=watercooler.association_id))
        session.flush()

        response = self.app.post(
            '/association/{0}/invite_user'.format(watercooler.association_id),
            data={'email': 'not a valid email'})
        eq_(response.status_code, 200)
        body = json.loads(response.data)
        eq_(body, {'status': 'error',
                   'error': "invalid email address 'not a valid email'"})

    def test_accept_invite_prompts_for_login(self):
        session = Client().session()
        association = Association(name="tower of power")
        session.add(association)
        session.flush()
        invite = AssociationInvite.generate(association.association_id,
                                            'fng@ema.il')
        session.flush()
        response = self.app.get('/accept_invitation/{0}/'.format(invite.token))
        eq_(response.status_code, 200)
        assert 'Please create an account' in response.data,\
            "Response didn't prompt for login"

    @logged_in
    def test_accept_invite_while_logged_in(self, user):
        user.email = 'fng@ema.il'
        session = Client().session()
        association = Association(name="tower of power")
        session.add(association)
        session.flush()
        invite = AssociationInvite.generate(association.association_id,
                                            'fng@ema.il')
        session.flush()
        response = self.app.get('/accept_invitation/{0}/'.format(invite.token))
        eq_(response.status_code, 302, response.data)
        eq_(response.headers['Location'],
            'http://localhost/association/{0}'.format(association.association_id))
        user_association = session.query(UserAssociation).\
            filter(UserAssociation.user_id == user.user_id).\
            one()
        eq_(user_association.association_id, association.association_id)
        invites = session.query(AssociationInvite).all()
        eq_(invites, [])

    @logged_in
    def test_accept_invite_while_unverified_verifies_email(self, user):
        user.email = 'fng@ema.il'
        user.email_verified_at = None
        session = Client().session()
        association = Association(name="tower of power")
        session.add(association)
        session.flush()
        invite = AssociationInvite.generate(association.association_id,
                                            'fng@ema.il')
        session.flush()
        response = self.app.get('/accept_invitation/{0}/'.format(invite.token))
        eq_(response.status_code, 302, response.data)
        del(user)
        user = session.query(User).one()
        assert user.email_verified_at, "Email wasn't verified"

    @logged_in
    def test_accept_invite__invalid_token(self, user):
        response = self.app.get('/accept_invitation/cafebabe/')
        eq_(response.status_code, 404, response.data)
