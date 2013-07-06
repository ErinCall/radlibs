from __future__ import unicode_literals

import datetime


def utcnow():
    return datetime.datetime.utcnow().strftime('%Y%m%d %H:%M:%S+00')
