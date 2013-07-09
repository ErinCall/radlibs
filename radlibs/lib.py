from __future__ import unicode_literals

from flask import g
from radlibs import Client
from radlibs.web import app
from radlibs.table.radlib import Rad, Lib


def load_lib(lib_name):
    lib_key = '{0}:{1}'.format(g.association_id, lib_name)
    lib = app.cache.get(lib_key)
    if not lib:
        session = Client().session()
        lib = session.query(Rad.rad).\
            join(Lib, Lib.lib_id == Rad.lib_id).\
            filter(Lib.name == lib_name).\
            filter(Lib.association_id == g.association_id).\
            all()

        if not lib:
            raise KeyError(lib_name)
        lib = [rad[0] for rad in lib]
        app.cache.set(lib_key, lib)
    return lib


def decache_lib(lib_name, association_id):
    Client().session().flush()
    lib_key = '{0}:{1}'.format(association_id, lib_name)
    app.cache.delete(lib_key)
