from __future__ import unicode_literals

from flask import url_for
from radlibs.table.association import Association


def breadcrumbs(*args):
    crumbs = [('Associations', url_for('list_associations'))]
    for value in args:
        crumbs.append(breadcrumb_for(value))
    return crumbs


def breadcrumb_for(value):
    if isinstance(value, basestring):
        return (value, None)
    if isinstance(value, Association):
        return (value.name,
                url_for('manage_association', association_id=value.association_id))
    else:
        raise TypeError("Don't know how to build a breadcrumb for {0}".value)
