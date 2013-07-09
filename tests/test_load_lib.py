from __future__ import unicode_literals

from nose.tools import eq_, raises
from mock import patch
from radlibs import Client
import radlibs.lib
from radlibs.table.user import User
from radlibs.table.association import Association
from radlibs.table.radlib import Rad, Lib
from tests import TestCase


class TestLoadLib(TestCase):
    @patch('radlibs.lib.g')
    def test_load_lib(self, g):
        session = Client().session()
        association = Association(name="partytown")
        session.add(association)
        session.flush()

        food = Lib(name='Food', association_id=association.association_id)
        rant = Lib(name='Rant', association_id=association.association_id)
        session.add(food)
        session.add(rant)

        user = User()
        session.add(user)
        session.flush()

        session.add(Rad(created_by=user.user_id,
                        rad='chili con carne',
                        lib_id=food.lib_id))
        session.add(Rad(created_by=user.user_id,
                        rad='bread',
                        lib_id=food.lib_id))
        session.add(Rad(created_by=user.user_id,
                        rad="It's insane, this guy's <Body_part>",
                        lib_id=rant.lib_id))
        session.flush()

        g.association_id = association.association_id
        lib = radlibs.lib.load_lib('Food')

        eq_(lib, ['chili con carne', 'bread'])

    @patch('radlibs.lib.g')
    def test_load_lib__two_associations_have_the_same_lib_name(self, g):
        session = Client().session()
        partytown = Association(name="partytown")
        watercooler = Association(name="watercooler")
        session.add(watercooler)
        session.add(partytown)
        session.flush()

        party_food = Lib(name='Food', association_id=partytown.association_id)
        water_food = Lib(name='Food', association_id=watercooler.association_id)
        session.add(party_food)
        session.add(water_food)

        user = User()
        session.add(user)
        session.flush()

        session.add(Rad(created_by=user.user_id,
                        rad='bubble tea',
                        lib_id=water_food.lib_id))
        session.add(Rad(created_by=user.user_id,
                        rad='cake',
                        lib_id=party_food.lib_id))
        session.flush()

        g.association_id = watercooler.association_id
        lib = radlibs.lib.load_lib('Food')

        eq_(lib, ['bubble tea'])

    @raises(KeyError)
    @patch('radlibs.lib.g')
    def test_no_such_lib_raises_keyerror(self, g):
        session = Client().session()
        association = Association(name="prancing ponies")
        session.add(association)
        session.flush()
        g.association_id = association.association_id

        radlibs.lib.load_lib('Loot')
