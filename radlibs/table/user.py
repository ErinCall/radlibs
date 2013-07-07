from __future__ import unicode_literals

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
from uuid import uuid4 as uuid
from radlibs import Client


class User(Base):
    __tablename__ = 'user'
    user_id = Column(Integer, primary_key=True)
    email = Column(String)
    identifier = Column(String)
    email_verified_at = Column(DateTime)
    api_key = Column(String)


class EmailVerificationToken(Base):
    __tablename__ = 'email_verification_token'
    user_id = Column(Integer, ForeignKey(User.user_id))
    token = Column(String, primary_key=True)

    @classmethod
    def generate(cls, user):
        session = Client().session()
        token = uuid()
        verification_token = cls(token=token.hex, user_id=user.user_id)
        session.add(verification_token)
        return verification_token
