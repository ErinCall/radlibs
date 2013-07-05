from __future__ import unicode_literals

from nose.tools import eq_
from tests import TestCase, logged_in
from radlibs.table.association import Association, UserAssociation
from radlibs.table.user import User
from radlibs import Client


class TestAssociation(TestCase):
    @logged_in
    def test_association_list_redirects_to_create_if_user_has_none(self, user):
        response = self.app.get('/list_associations')
        eq_(response.status_code, 302, response.data)

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
        response = self.app.get('/list_associations')

        eq_(response.status_code, 200, response.data)
        assert 'watercooler' in response.data, response.data
        assert 'codescouts' in response.data, response.data
        assert 'create a new association' in response.data, response.data

    @logged_in
    def test_create_new_association(self, user):
        session = Client().session()
        response = self.app.post('/new_association',
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
