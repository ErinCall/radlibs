from __future__ import unicode_literals

import sha
import json
import datetime
from mock import patch, Mock
from nose.tools import eq_
from radlibs.table.user import User, EmailVerificationToken
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
        assert user.email_verified_at, "User email wasn't verified"

    @patch('radlibs.web.controllers.login.send_verification_mail')
    @patch('radlibs.web.controllers.login.os')
    @patch('radlibs.web.controllers.login.requests')
    def test_log_in_with_a_provider_that_does_not_supply_email(
            self, requests, os, send_verification_mail):
        session = Client().session()
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

        user = session.query(User).one()
        eq_(user.email, 'tpain@umg.com')
        eq_(user.identifier, 'twitter.com/tpain')
        eq_(user.email_verified_at, None)

        token = session.query(EmailVerificationToken).one()
        send_verification_mail.assert_called_once_with(
            user,
            'http://localhost/verify_email/{0}'.format(token.token))

    def test_verify_email(self):
        session = Client().session()
        user = User()
        session.add(user)
        session.flush()
        token = EmailVerificationToken.generate(user)

        response = self.app.get('/verify_email/{0}'.format(token.token))
        eq_(response.status_code, 200, response.data)
        assert 'Thanks!' in response.data, 'response was rude'

        del(user)
        user = session.query(User).one()
        assert user.email_verified_at, "email wasn't verified!"

        tokens = session.query(EmailVerificationToken).all()
        eq_(tokens, [])

    def test_verify_email__invalid_token(self):
        response = self.app.get('/verify_email/badcafe')
        eq_(response.status_code, 404, response.data)

    @patch('radlibs.web.controllers.login.os')
    @patch('radlibs.web.controllers.login.requests')
    def test_error_when_a_user_uses_the_wrong_identifier(self, requests, os):
        os.environ = {'ENGAGE_API_KEY': 'aoeu'}
        response = Mock()
        session = Client().session()
        user = User(email='withintemptation@umg.com',
                    identifier='http://www.twitter.com/withintemptation')
        session.add(user)
        session.flush()

        requests.get.return_value = response
        response.text = json.dumps({
            'profile': {
                'email': 'withintemptation@umg.com',
                'identifier': 'facebook.com/withintemptation',
            }
        })
        response = self.app.post(
            '/token_url',
            data={'token': 'asdf', 'redirect_uri': '/language'})
        eq_(response.status_code, 200, response.data)
        assert 'Maybe you meant to log in with Twitter?' in response.data,\
               response.data

    def test_authenticate_with_hmac_signature(self):
        session = Client().session()
        user = User(api_key='hurfdurf')
        session.add(user)
        session.flush()
        time = datetime.datetime.utcnow().strftime('%Y%m%d %H:%M:%S')
        endpoint = '/test_authorization'
        plaintext = "{0}\nother_param: frabjous\n{1}\n{2}".format(
            time, endpoint, 'hurfdurf')
        signature = sha.sha(plaintext).hexdigest()
        response = self.app.post(
            endpoint, data={'user_id': user.user_id,
                            'signature': signature,
                            'time': time,
                            'other_param': 'frabjous'})
        eq_(response.status_code, 200, response.data)
        body = json.loads(response.data)
        eq_(body, {'status': 'ok'})

    def test_authenticate_with_hmac_signature__no_such_user_id(self):
        response = self.app.post(
            '/test_authorization', data={'user_id': 8,
                                         'signature': 'woop woop',
                                         'time': '20130706 08:29:00',
                                         'other_param': 'frabjous'})
        eq_(response.status_code, 200, response.data)
        body = json.loads(response.data)
        eq_(body, {'status': 'error', 'error': 'not logged in'})

    def test_hmac_auth__user_has_no_api_key(self):
        session = Client().session()
        user = User()
        session.add(user)
        session.flush()
        time = datetime.datetime.utcnow().strftime('%Y%m%d %H:%M:%S')
        signature = "mloop droop"
        response = self.app.post(
            '/test_authorization', data={'user_id': user.user_id,
                                         'signature': signature,
                                         'time': time,
                                         'other_param': 'frabjous'})
        eq_(response.status_code, 200, response.data)
        body = json.loads(response.data)
        eq_(body, {'status': 'error', 'error': 'not logged in'})

    def test_hmac_auth__time_must_be_within_five_minutes_of_server(self):
        session = Client().session()
        user = User(api_key='hurfdurf')
        session.add(user)
        session.flush()
        time = '20010101 01:01:01'
        endpoint = '/test_authorization'
        plaintext = "{0}\nother_param: frabjous\n{1}\n{2}".format(
            time, endpoint, 'hurfdurf')
        signature = sha.sha(plaintext).hexdigest()
        response = self.app.post(
            endpoint, data={'user_id': user.user_id,
                            'signature': signature,
                            'time': time,
                            'other_param': 'frabjous'})
        eq_(response.status_code, 200, response.data)
        body = json.loads(response.data)
        eq_(body, {'status': 'error', 'error': 'not logged in'})

    def test_hmac_auth__invalid_datetime_format(self):
        session = Client().session()
        user = User(api_key='hurfdurf')
        session.add(user)
        session.flush()
        response = self.app.post(
            '/test_authorization', data={'user_id': user.user_id,
                                         'signature': 'johnhancock',
                                         'time': 'beer:30',
                                         'other_param': 'frabjous'})
        eq_(response.status_code, 200, response.data)
        body = json.loads(response.data)
        eq_(body, {'status': 'error', 'error': 'not logged in'})
