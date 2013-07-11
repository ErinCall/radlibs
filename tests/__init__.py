from __future__ import unicode_literals

import os
import subprocess
import time
from functools import wraps
from sqlalchemy.exc import ProgrammingError
from sqlalchemy import create_engine
from flask import appcontext_pushed, g
from werkzeug.contrib.cache import NullCache

import radlibs
from radlibs.web import app
from radlibs.table.user import User

import unittest
from mock import patch


class TestCase(unittest.TestCase):
    def setUp(self):
        radlibs.Client()._engine = db_info['engine']
        radlibs.Client().session().commit = radlibs.Client().session().flush
        app.secret_key = str('super sekret')
        self.app = app.test_client()

    def tearDown(self):
        radlibs.Client().session().rollback()


db_info = {}


def setUpPackage():
    app.config['SERVER_NAME'] = 'localhost'
    create_temp_database()
    temp_db_url = 'postgresql://localhost/%s' % db_info['temp_db_name']
    db_info['engine'] = create_engine(temp_db_url)
    app.cache = NullCache()

    apply_migrations(temp_db_url)


def tearDownPackage():
    terminate_query = """
        select pg_terminate_backend( %(pid_column)s )
        from pg_stat_activity
        where datname = '%(db_name)s'
    """
    try:
        db_info['master_engine'].execute(terminate_query % {
            'pid_column': 'procpid',
            'db_name': db_info['temp_db_name'],
        })
    except ProgrammingError as e:
        if '"procpid" does not exist' in str(e):
            #postgres 9.2 changed pg_stat_activity.procpid to just .pid
            db_info['master_engine'].execute(terminate_query % {
                'pid_column': 'pid',
                'db_name': db_info['temp_db_name'],
            })
        else:
            raise
    drop_temp_database()


def create_temp_database():
    db_info['master_engine'] = create_engine('postgresql://localhost/postgres')
    db_info['temp_db_name'] = 'radlibs_test_%d' % int(time.time())
    conn = db_info['master_engine'].connect()
    conn.execute('commit')  # work around sqlalchemy's auto-transactions
    conn.execute('create database %s' % db_info['temp_db_name'])


def drop_temp_database():
    conn = db_info['master_engine'].connect()
    conn.execute('commit')
    conn.execute('drop database %s' % db_info['temp_db_name'])


def apply_migrations(temp_db_url):
    migrations_dir = os.path.join(
        os.path.dirname(__file__), '..', 'migrations')
    subprocess.check_output([
        'yoyo-migrate', '-b', 'apply', migrations_dir, temp_db_url])


def with_libs(libs):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            load_lib = lambda lib_name: libs[lib_name]
            with patch('radlibs.parser.load_lib', load_lib):
                fn(*args, **kwargs)
        return wrapper
    return decorator


def with_config(**kwargs):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **inner_kwargs):
            orig_config = {}
            for key, value in kwargs.iteritems():
                orig_config[key] = app.config[key]
                app.config[key] = value
            try:
                return fn(*args, **inner_kwargs)
            finally:
                for key, value in kwargs.iteritems():
                    app.config[key] = orig_config[key]
        return wrapper
    return decorator


def logged_in(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = User(email="adele@umg.com", identifier="facebook.com/adele")
        radlibs.Client().session().add(user)

        def handler(sender, **kwargs):
            g.user = user
        with appcontext_pushed.connected_to(handler, app):
            args = args + (user,)
            fn(*args, **kwargs)
    return wrapper
