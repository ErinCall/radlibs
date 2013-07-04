from __future__ import unicode_literals

from unittest import TestCase
from nose.tools import eq_

from radlibs.parser import parse, Text, Lib


class TestParser(TestCase):
    def test_just_a_string(self):
        plaintext = "no remorse, 'cause I still remember"
        rad = parse(plaintext)
        eq_(rad, [plaintext])
        eq_(type(rad[0]), Text)

    def test_just_a_lib(self):
        plaintext = "<Song>"
        rad = parse(plaintext)

        eq_(rad, ['Song'])
        eq_(type(rad[0]), Lib)
        eq_(rad[0].lib, [
            'Black Skinhead',
            'Blood On The Leaves',
            ])

    def test_a_libs_and_text_intermingled(self):
        plaintext = "the <Animal> ate my <Loot>"

        rad = parse(plaintext)
        eq_(rad, ['the ', 'Animal', ' ate my ', 'Loot'])
        eq_(rad[1].lib, [
            'cat',
            'dog',
            'buffoon'])
        eq_(rad[3].lib, [
            'potion of booze',
            '+5 sword of sharpness'])

    def test_literal_angle_brackets(self):
        plaintext = "look over there --\>"

        rad = parse(plaintext)
        eq_(rad, ['look over there -->'])