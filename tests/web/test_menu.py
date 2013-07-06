from __future__ import unicode_literals

from mock import patch, Mock
from nose.tools import eq_
from tests import TestCase, logged_in
from radlibs.web import build_menu


class TestMenu(TestCase):
    def test_when_logged_out(self):
        g = Mock()
        g.user = None
        with patch('radlibs.web.g', g):
            eq_(build_menu(), {
                'menu': [
                    ('live_demo', 'Try It Live'),
                    ('language', 'The Language'),
                ]})
        response = self.app.get('/')
        assert 'Try It Live' in response.data, "didn't see try it"
        assert 'The Language' in response.data, "didn't see language"
        assert 'Sign In' in response.data, "didn't see signin link"

    @logged_in
    def test_when_logged_in(self, user):
        g = Mock()
        g.user = user
        with patch('radlibs.web.g', g):
            eq_(build_menu(), {
                'menu': [
                    ('live_demo', 'Try It Live'),
                    ('language', 'The Language'),
                    ('list_associations', 'Manage Associations'),
                ]})
        response = self.app.get('/')
        assert "Try It Live" in response.data, "didn't see try it"
        assert 'The Language' in response.data, "didn't see language"
        assert 'Manage Associations' in response.data, "didn't see manage"
        assert 'Log out' in response.data, "didn't see logout link"
