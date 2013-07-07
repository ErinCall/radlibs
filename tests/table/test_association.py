from __future__ import unicode_literals

from radlibs import Client
from tests import TestCase
from nose.tools import eq_
from radlibs.table.association import (
    Association,
    UserAssociation,
    AssociationInvite)
from radlibs.table.user import User


class TestAssociation(TestCase):
    def test_find_all_for_user(self):
        session = Client().session()
        prancing_ponies = Association(name='prancing ponies')
        watercooler = Association(name='watercooler')
        rtk = Association(name='rtk')
        session.add(prancing_ponies)
        session.add(watercooler)
        session.add(rtk)

        user = User(email="joe@janra.in")
        session.add(user)
        session.flush()

        session.add(UserAssociation(
            association_id=prancing_ponies.association_id,
            user_id=user.user_id))
        session.add(UserAssociation(
            association_id=watercooler.association_id,
            user_id=user.user_id))
        session.flush()

        associations = Association.find_all_for_user(user)

        eq_(associations, [prancing_ponies, watercooler])


class TestAssociationInvite(TestCase):
    def test_generate(self):
        session = Client().session()
        association = Association(name='crazy train')
        session.add(association)
        session.flush()

        invite = AssociationInvite.generate(association.association_id,
                                            'nothingtolose@rhythmandblu.es')
