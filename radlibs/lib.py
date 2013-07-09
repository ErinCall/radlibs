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
        #does this look wrong? I think so too. There is a bug in the werkzeug
        #redis cache library where it reverses the timeout and value arguments
        #to redis.setex.
        #and of course we need to manually call dump_object, which the cache
        #would normally do for us, because it messes up and calls dump_object
        #on the timeout...
        app.cache.set(lib_key, 60*60, timeout=app.cache.dump_object(lib))
    return lib


def decache_lib(lib_name, association_id):
    Client().session().flush()
    lib_key = '{0}:{1}'.format(association_id, lib_name)
    app.cache.delete(lib_key)
