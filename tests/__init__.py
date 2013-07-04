from __future__ import unicode_literals

import os
import subprocess
import time
from functools import wraps
from sqlalchemy import create_engine

import radlibs

import unittest
from mock import patch


class TestCase(unittest.TestCase):
    def setUp(self):
        radlibs.Client()._engine = db_info['engine']
        radlibs.Client().session().commit = radlibs.Client().session().flush

    def tearDown(self):
        radlibs.Client().session().rollback()


db_info = {}

def setUpPackage():
    create_temp_database()
    temp_db_url = 'postgresql://localhost/%s' % db_info['temp_db_name']
    db_info['engine'] = create_engine(temp_db_url)

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
    except sqlalchemy.exc.ProgrammingError as e:
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
    conn.execute('commit')#work around sqlalchemy's auto-transactions
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