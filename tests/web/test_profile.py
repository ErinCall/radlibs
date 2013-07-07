from __future__ import unicode_literals

from nose.tools import eq_
from tests import TestCase, logged_in

from radlibs import Client
from radlibs.table.user import User


class TestProfile(TestCase):
    @logged_in
    def test_profile(self, user):
        user.api_key = 'froufruraw'
        response = self.app.get('/profile')
        eq_(response.status_code, 200)
        assert user.email in response.data, "didn't see email"
        assert 'froufruraw' in response.data, "didn't see api key"

    def test_profile__login_required(self):
        response = self.app.get('/profile')
        eq_(response.status_code, 401)

    @logged_in
    def test_get_an_api_key(self, user):
        response = self.app.post('/profile/get_api_key')
        eq_(response.status_code, 302)
        eq_(response.headers['Location'], 'http://localhost/profile')

        del(user)
        user = Client().session().query(User).one()
        assert user.api_key, "user didn't get an api key"

    def test_get_an_api_key_requires_login(self):
        response = self.app.post('/profile/get_api_key')
        eq_(response.status_code, 401)
