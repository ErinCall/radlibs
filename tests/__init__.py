from __future__ import unicode_literals

from mock import patch
from functools import wraps

def with_libs(libs):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            load_lib = lambda lib_name: libs[lib_name]
            with patch('radlibs.parser.load_lib', load_lib):
                fn(*args, **kwargs)
        return wrapper
    return decorator