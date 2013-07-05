from __future__ import unicode_literals

import json
from mock import patch, Mock
from nose.tools import eq_
from radlibs.table.user import User
from radlibs import Client
from tests import TestCase


class TestLogin(TestCase):
    @patch('radlibs.web.controllers.login.os')
    @patch('radlibs.web.controllers.login.requests')
    def test_log_in(self, requests, os):
        os.environ = {'ENGAGE_API_KEY': 'aoeu'}
        response = Mock()
        requests.get.return_value = response
        response.text = json.dumps({
            'profile': {
                'identifier': 'facebook.com/andrew',
                'email': 'andrew@myema.il',
            }
        })
        session = Client().session()
        user = User(email="andrew@myema.il",
                    identifier="facebook.com/andrew")
        session.add(user)
        session.flush()

        response = self.app.post('/token_url',
                                 data={'token': 'asdf', 'redirect_uri': '/live_demo'})
        requests.get.assert_called_with('https://rpxnow.com/api/v2/auth_info',
                                        params={'token': 'asdf',
                                                'format': 'json',
                                                'apiKey': 'aoeu'})
        eq_(response.status_code, 302)
        eq_(response.headers['Location'], 'http://localhost/live_demo')

    @patch('radlibs.web.controllers.login.os')
    @patch('radlibs.web.controllers.login.requests')
    def test_log_in_with_no_existing_user(self, requests, os):
        os.environ = {'ENGAGE_API_KEY': 'aoeu'}
        response = Mock()
        requests.get.return_value = response
        response.text = json.dumps({
            'profile': {
                'identifier': 'facebook.com/yeezy',
                'email': 'yeezy@umg.com',
            }
        })
        response = self.app.post('/token_url', data={'token': 'asdf'})
        eq_(response.status_code, 302)
        eq_(response.headers['Location'], 'http://localhost/')

        user = Client().session().query(User).one()
        eq_(user.email, 'yeezy@umg.com')
        eq_(user.identifier, 'facebook.com/yeezy')

    @patch('radlibs.web.controllers.login.os')
    @patch('radlibs.web.controllers.login.requests')
    def test_log_in_with_a_provider_that_does_not_supply_email(self,
                                                               requests,
                                                               os):
        os.environ = {'ENGAGE_API_KEY': 'aoeu'}
        response = Mock()
        requests.get.return_value = response
        response.text = json.dumps({
            'profile': {
                'identifier': 'twitter.com/tpain',
            }
        })
        response = self.app.post(
            '/token_url',
            data={'token': 'asdf', 'redirect_uri': '/language'})
        eq_(response.status_code, 302)
        eq_(response.headers['Location'],
            'http://localhost/complete_registration?redirect_uri=%2Flanguage')

        response = self.app.get('/complete_registration',
                                data={'redirect_uri': '/language'})
        eq_(response.status_code, 200, response.data)
        response = self.app.post('/complete_registration', data={
            'redirect_uri': '/language',
            'email': 'tpain@umg.com'})
        eq_(response.status_code, 302, response.data)
        eq_(response.headers['Location'], 'http://localhost/language')

        user = Client().session().query(User).one()
        eq_(user.email, 'tpain@umg.com')
        eq_(user.identifier, 'twitter.com/tpain')
