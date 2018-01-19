#!/usr/bin/python2.7
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    # add serialize function to send JSON objects in a serializable format
    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
        }


class Item(Base):
    __tablename__ = 'item'

    title = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey('category.id'))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    # add serialize function to send JSON objects in a serializable format
    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'cat_id': self.category_id,
            'description': self.description
        }


engine = create_engine('postgresql://catalog:catalog@localhost/categoryitemwithusers')


Base.metadata.create_all(engine)
