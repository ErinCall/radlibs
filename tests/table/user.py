from __future__ import unicode_literals

from nose.tools import eq_
from tests import TestCase
from radlibs import Client
from radlibs.table.user import User, EmailVerificationToken


class TestVerificationTokens(TestCase):
    def test_generate_token(self):
        session = Client().session()
        user = User()
        session.add(user)
        session.flush()

        token = EmailVerificationToken.generate(user)
        eq_(len(token.token), 32)
