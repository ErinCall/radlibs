from __future__ import unicode_literals

from nose.tools import eq_
from flask import current_app
from tests import TestCase
from radlibs.table.association import Association, UserAssociation
from radlibs.table.user import User
from radlibs.table.radlib import Rad, Lib
from radlibs import Client
from radlibs.web import app
from radlibs.web.breadcrumbs import breadcrumbs, breadcrumb_for


class TestBreadCrumbs(TestCase):
    def test_just_a_string(self):
        with app.app_context():
            crumbs = breadcrumbs('Blammo')
        eq_(crumbs, [
            ('Associations', 'http://localhost/associations'),
            ('Blammo', None)])

    def test_breadcrumb_for_an_association(self):
        session = Client().session()
        association = Association(name="Harpy")
        session.add(association)
        session.flush()
        with app.app_context():
            crumb = breadcrumb_for(association)
        eq_(crumb, ('Harpy', 'http://localhost/association/{0}'.format(
            association.association_id)))
