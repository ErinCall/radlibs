from __future__ import unicode_literals

from mock import patch
from nose.tools import eq_, assert_raises

from radlibs.parser import parse, Text, Lib, ParseError

from tests import TestCase, with_libs


def test_libs():
    return {
        'Animal': ['cat'],
        'Loot': ['blessed longsword'],
        'Look': ['look: <Animal>'],
        'Song_which_never_ends': ["""this is the song which never ends,
yes it goes on and on my friend
some people started singing it not knowing what it was
and they'll continue singing it forever just because
<Song_which_never_ends>"""],
    }


class TestParser(TestCase):
    def test_just_a_string(self):
        plaintext = "no remorse, 'cause I still remember"
        rad = parse(plaintext)
        eq_(rad, plaintext)
        eq_(type(rad.children[0]), Text)

    def test_an_empty_string(self):
        plaintext = ''
        rad = parse(plaintext)
        eq_(rad, plaintext)

    @with_libs(test_libs())
    def test_just_a_lib(self):
        plaintext = "<Animal>"
        rad = parse(plaintext)

        eq_(unicode(rad), 'cat')
        eq_(type(rad.children[0]), Lib)

    @with_libs(test_libs())
    def test_libs_and_text_intermingled(self):
        plaintext = "the <Animal> ate my <Loot>"

        rad = parse(plaintext)
        eq_(rad, 'the cat ate my blessed longsword')
        eq_(rad.children, ['the',
                           ' ',
                           'cat',
                           ' ',
                           'ate',
                           ' ',
                           'my',
                           ' ',
                           'blessed longsword'])

    def test_literal_angle_brackets(self):
        plaintext = "look over there --\>"

        rad = parse(plaintext)
        eq_(rad, 'look over there -->')

    @with_libs(test_libs())
    def test_recursion_depth_is_limited(self):
        plaintext = '<Song_which_never_ends>'
        rad = parse(plaintext)
        radlib = unicode(rad)
        assert len(radlib) > 3000, radlib
        assert len(radlib) < 9000, radlib

    @with_libs(test_libs())
    def test_parse_error(self):
        plaintext = 'error>'
        with assert_raises(ParseError) as error:
            parse(plaintext)
        eq_(error.exception.message,
            "Unexpected token '>' at line 1 character 6 of 'error>'")

    def test_deeply_nested_parse_error(self):
        libs = {
            'Outermost': ['into <Middle>'],
            'Middle': ['into <Inner>'],
            'Inner': ['into <Broken>'],
            'Broken': ['HAY GUISE>'],
        }
        load_lib = lambda lib_name: libs[lib_name]
        with patch('radlibs.parser.load_lib', load_lib):
            with assert_raises(ParseError) as error:
                print unicode(parse('<Outermost>'))

        eq_(error.exception.message,
            "Unexpected token '>' at line 1 character 10 of 'HAY GUISE>' "
            "(found inside Broken) (found inside Inner) (found inside Middle) "
            "(found inside Outermost)")

    def test_a_literal_d_not_after_a_lib(self):
        plaintext = 'betted'
        eq_(parse(plaintext), plaintext)

    def test_a_literal_d_after_a_lib(self):
        libs = {'Verb': ['run']}

        with patch('radlibs.parser.load_lib', lambda lib: libs[lib]):
            radlib = unicode(parse('<Verb>\\d'))

        eq_(radlib, "rund")

    def test_past_tense__simple_case(self):
        libs = {
            'Verb': ['pounce'],
        }
        with patch('radlibs.parser.load_lib', lambda lib: libs[lib]):
            radlib = unicode(parse('I <Verb>d quickly'))

        eq_(radlib, "I pounced quickly")

    def test_past_tense__irregular_verb(self):
        libs = {'Verb': ['run']}
        with patch('radlibs.parser.load_lib', lambda lib: libs[lib]):
            radlib = unicode(parse('I <Verb>d quickly'))

        eq_(radlib, "I ran quickly")

    def test_past_tense__verb_phrase(self):
        libs = {'Verb': ['run^ quickly']}
        with patch('radlibs.parser.load_lib', lambda lib: libs[lib]):
            radlib = unicode(parse('I <Verb>d'))
        eq_(radlib, "I ran quickly")

    def test_past_tense__in_a_nested_lib(self):
        libs = {
            'Verb': ['run'],
            'Action': ['I <Verb>^ quickly'],
        }

        with patch('radlibs.parser.load_lib', lambda lib: libs[lib]):
            radlib = unicode(parse('sometimes <Action>d'))

        eq_(radlib, 'sometimes I ran quickly')

    def test_a_literal_s_not_after_a_lib(self):
        radlib = unicode(parse('parts'))
        eq_(radlib, 'parts')

    def test_a_literal_s_after_a_lib(self):
        libs = {'Loot': ['sword^ of slaying']}
        with patch('radlibs.parser.load_lib', lambda lib: libs[lib]):
            radlib = unicode(parse('<Loot>\\s'))

        eq_(radlib, 'sword of slayings')

    def test_plural__simple_case(self):
        libs = {'Loot': ['sword']}
        with patch('radlibs.parser.load_lib', lambda lib: libs[lib]):
            radlib = unicode(parse('<Loot>s'))

        eq_(radlib, 'swords')

    def test_plural__irregular_noun(self):
        libs = {'Animal': ['sheep']}
        with patch('radlibs.parser.load_lib', lambda lib: libs[lib]):
            radlib = unicode(parse('<Animal>s'))

        eq_(radlib, 'sheep')

    def test_plural__verb_phrase(self):
        libs = {'Loot': ['sword^ of slaying']}
        with patch('radlibs.parser.load_lib', lambda lib: libs[lib]):
            radlib = unicode(parse('<Loot>s'))
        eq_(radlib, "swords of slaying")

    def test_plural__in_a_nested_lib(self):
        libs = {
            'Loot': ['sword^ of slaying'],
            'Treasure': ['You find 3 <Loot>s in the chest!'],
        }

        with patch('radlibs.parser.load_lib', lambda lib: libs[lib]):
            radlib = unicode(parse('After defeating the monster, <Treasure>'))

        eq_(radlib, 'After defeating the monster, '
            'You find 3 swords of slaying in the chest!')

