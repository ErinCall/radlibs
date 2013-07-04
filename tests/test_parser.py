from unittest import TestCase
from nose.tools import eq_

from radlibs.parser import parse, Text, Lib


class TestParser(TestCase):
    def test_just_a_string(self):
        plaintext = "no remorse, 'cause I still remember"
        rad = parse(plaintext)
        eq_(rad, [plaintext])
        eq_(type(rad[0]), Text)

    def test_just_a_dictionary(self):
        plaintext = "<Song>"
        rad = parse(plaintext)

        eq_(rad, ['Song'])
        eq_(type(rad[0]), Lib)
