from __future__ import unicode_literals


from flask import g
from mock import Mock, patch
from nose.tools import eq_
from tests import TestCase
from radlibs.web import app
from radlibs.mail import send_verification_mail, send_invitation_mail
from radlibs.table.user import User


class TestSendVerificationMail(TestCase):
    @patch('radlibs.mail.smtplib')
    @patch('radlibs.mail.os')
    def test_send_verification_mail(self, os, smtplib):
        os.environ = {'SENDGRID_PASSWORD': 'letmein',
                      'SENDGRID_USERNAME': 'itsme'}
        app.config['SERVER_NAME'] = 'localhost:5000'
        smtp = Mock()
        smtplib.SMTP.return_value = smtp
        user = User(email="newuser@ema.il")
        with app.test_request_context('/'):
            g.user = user
            send_verification_mail(user, 'http://radlibs.info/verify/asdf')

        smtp.sendmail.assert_called_once()
        from_address, to_addresses, message = smtp.sendmail.mock_calls[0][1]
        eq_(from_address, 'support@radlibs.info')
        eq_(to_addresses, ['newuser@ema.il'])
        assert 'http://radlibs.info/verify/asdf' in message,\
            "Didn't see verification url"
        assert '<a href="http://radlibs.info/verify/asdf">' in message,\
            "Didn't see verification link"


class TestSendInvitationEmail(TestCase):
    @patch('radlibs.mail.smtplib')
    @patch('radlibs.mail.os')
    def test_send_verification_mail(self, os, smtplib):
        os.environ = {'SENDGRID_PASSWORD': 'letmein',
                      'SENDGRID_USERNAME': 'itsme'}
        app.config['SERVER_NAME'] = 'localhost:5000'
        smtp = Mock()
        smtplib.SMTP.return_value = smtp
        user = User(email="newuser@ema.il")
        with app.test_request_context('/'):
            g.user = user
            send_invitation_mail('friend@ema.il',
                                 'invitey@emai.il',
                                 'codescouts',
                                 'http://radlibs.info/accept_invitation/asdf')
        smtp.sendmail.assert_called_once()
        from_address, to_addresses, message = smtp.sendmail.mock_calls[0][1]
        eq_(from_address, 'welcome@radlibs.info')
        eq_(to_addresses, ['friend@ema.il'])
        print message
        assert 'http://radlibs.info/accept_invitation/asdf' in message,\
            "Didn't see acceptance url"
        assert '<a href="http://radlibs.info/accept_invitation/asdf">' in message,\
            "Didn't see acceptance link"
