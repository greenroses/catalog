#!/usr/bin/python2.7
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Item, Category
import time

engine = create_engine('postgresql://catalog:catalog@localhost/categoryitemwithusers')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# create dummy users
User1 = User(name="greenroses", email="greenroses@udacity.com",
             picture='https://upload.wikimedia.org/wikipedia/commons/e/e6/Rosa_rubiginosa_1.jpg')  # noqa
session.add(User1)
session.commit()

# create category and items
category1 = Category(user_id=1, name="Snowboarding")
session.add(category1)
session.commit()

item1 = Item(user_id=1, title="Goggles",
             description="Goggles are forms of protective eyeware",
             category=category1)
session.add(item1)
session.commit()

item2 = Item(user_id=1, title="Snowboard",
             description="Snowboard is for snowboarding", category=category1)
session.add(item2)
session.commit()

# create category and items
category1 = Category(user_id=1, name="Running")
session.add(category1)
session.commit()

item1 = Item(user_id=1, title="Water",
             description="Drink a lot of water when you are thirsty",
             category=category1)
session.add(item1)
session.commit()

item2 = Item(user_id=1, title="Shoes",
             description="A pair of comfortable running shoes" +
             "makes running more fun",
             category=category1)
session.add(item2)
session.commit()

item3 = Item(user_id=1, title="Sunshine",
             description="Sunny days are best for running",
             category=category1)
session.add(item3)
session.commit()

# create category and items
category1 = Category(user_id=1, name="Frisbee")
session.add(category1)
session.commit()

item1 = Item(user_id=1, title="Frisbee", description="Frisbee is fun",
             category=category1)
session.add(item1)
session.commit()

item2 = Item(user_id=1, title="Friends",
             description="Play frisbee with friends",
             category=category1)
session.add(item2)
session.commit()

item3 = Item(user_id=1, title="Dogs", description="Play frisbee with dogs",
             category=category1)
session.add(item3)
session.commit()

# create category and items
category1 = Category(user_id=1, name="Baseball")
session.add(category1)
session.commit()

item1 = Item(user_id=1, title="Bat", description="Bats are for baseball",
             category=category1)
session.add(item1)
session.commit()

item2 = Item(user_id=1, title="Baseball",
             description="A Baseball is a ball used in the sports of baseball",
             category=category1)
session.add(item2)
session.commit()

# create category and items
category1 = Category(user_id=1, name="Soccer")
session.add(category1)
session.commit()

category1 = Category(user_id=1, name="Basketball")
session.add(category1)
session.commit()

category1 = Category(user_id=1, name="Rock Climbing")
session.add(category1)
session.commit()

category1 = Category(user_id=1, name="Football")
session.add(category1)
session.commit()

category1 = Category(user_id=1, name="Skating")
session.add(category1)
session.commit()

category1 = Category(user_id=1, name="Hockey")
session.add(category1)
session.commit()

print "added category items!"
