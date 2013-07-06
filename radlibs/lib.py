from __future__ import unicode_literals

from flask import g
from radlibs import Client
from radlibs.table.radlib import Rad, Lib


def load_lib(lib_name):
    session = Client().session()
    lib = session.query(Rad.rad).\
        join(Lib, Lib.lib_id == Rad.lib_id).\
        filter(Lib.name == lib_name).\
        filter(Lib.association_id == g.association_id).\
        all()

    if not lib:
        raise KeyError(lib_name)
    return [x[0] for x in lib]
