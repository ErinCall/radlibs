from __future__ import unicode_literals

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class Singleton(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._instance


class Client(Singleton):
    _session = None
    _engine = None

    def session(self):
        if not self._engine:
            self._engine = create_engine(os.environ['DATABASE_URL'])
        if not self._session:
            self._session = sessionmaker(bind=self._engine)()
        return self._session
