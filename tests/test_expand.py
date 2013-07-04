from __future__ import unicode_literals

from tests import with_libs
from nose.tools import eq_

from radlibs.expand import expand

from tests import TestCase

def test_libs():
	return {
		'Animal': ['cat'],
		'Look': ['look: <Animal>'],
		'Song_which_never_ends': [ """this is the song which never ends,
yes it goes on and on my friend
some people started singing it not knowing what it was
and they'll continue singing it forever just because
<Song_which_never_ends>"""],
	}

class TestExpand(TestCase):
	@with_libs(test_libs())
	def test_expand_simply(self):
		plaintext = "<Look> look"
		eq_(expand(plaintext), 'look: cat look')

	@with_libs(test_libs())
	def test_recursion_depth_is_limited(self):
		plaintext = '<Song_which_never_ends>'
		song = expand(plaintext)

		assert len(song) > 3000, song
		assert len(song) < 9000, song
