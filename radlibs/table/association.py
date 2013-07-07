from __future__ import unicode_literals

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
from uuid import uuid4 as uuid
from radlibs import Client
from radlibs.table.user import User


class Association(Base):
    __tablename__ = 'association'
    association_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    @classmethod
    def find_all_for_user(cls, user):
        return Client().session().query(cls).\
            join(UserAssociation,
                 UserAssociation.association_id == cls.association_id).\
            filter(UserAssociation.user_id == user.user_id).\
            all()


class UserAssociation(Base):
    __tablename__ = 'user_association'
    association_id = Column(Integer,
                            ForeignKey(Association.association_id),
                            primary_key=True)
    user_id = Column(Integer, ForeignKey(User.user_id), primary_key=True)


class AssociationInvite(Base):
    __tablename__ = 'association_invite'
    association_id = Column(Integer,
                            ForeignKey(Association.association_id),
                            primary_key=True)
    email = Column(String, primary_key=True)
    token = Column(String, nullable=False)

    @classmethod
    def generate(cls, association_id, email):
        token = uuid()
        self = cls(association_id=association_id, email=email, token=token.hex)
        Client().session().add(self)
        return self
