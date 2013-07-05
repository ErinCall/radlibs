from __future__ import unicode_literals

from tests import TestCase
from radlibs import Client
from radlibs.table.association import Association
from radlibs.table.user import User
from radlibs.table.radlib import Rad, Lib


class TestRadLib(TestCase):
    def test_rad_created_at_is_set_automatically(self):
        session = Client().session()
        user = User(identifier='www.facebook.com/joshuajames',
                    email='joshuajames@umg.com')
        association = Association(name="next good time")
        session.add(user)
        session.add(association)
        session.flush()

        lib = Lib(name='Food', association_id=association.association_id)
        session.add(lib)
        session.flush()

        rad = Rad(rad='chili con carne',
                  lib_id=lib.lib_id,
                  created_by=user.user_id)
        session.add(rad)
        session.flush()

        assert rad.created_at
