from __future__ import unicode_literals

from flask import g
from radlibs import Client
from radlibs.table.radlib import Rad, Lib


LIBS = {}


def load_lib(lib_name):
    lib_key = '{0}:{1}'.format(g.association_id, lib_name)
    if lib_key not in LIBS:
        session = Client().session()
        lib = session.query(Rad.rad).\
            join(Lib, Lib.lib_id == Rad.lib_id).\
            filter(Lib.name == lib_name).\
            filter(Lib.association_id == g.association_id).\
            all()

        if not lib:
            raise KeyError(lib_name)
        LIBS[lib_key] = [x[0] for x in lib]
    return LIBS[lib_key]
