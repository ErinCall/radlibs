from __future__ import unicode_literals

import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
from radlibs.table.user import User
from radlibs.table.association import Association


class Lib(Base):
    __tablename__ = 'lib'
    lib_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    association_id = Column(Integer,
                            ForeignKey(Association.association_id),
                            nullable=False)


class Rad(Base):
    __tablename__ = 'rad'
    rad_id = Column(Integer, primary_key=True)
    rad = Column(String, nullable=False)
    lib_id = Column(Integer, ForeignKey(Lib.lib_id), nullable=False)
    created_by = Column(Integer, ForeignKey(User.user_id), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)

    def __init__(self, *args, **kwargs):
        super(Rad, self).__init__(*args, **kwargs)
        if self.created_at is None:
            self.created_at = datetime.datetime.utcnow().\
                strftime('%Y%m%d %H:%M:%S')