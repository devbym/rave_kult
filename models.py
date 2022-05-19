from sqlalchemy import (Column,DateTime,
                        ForeignKey, Integer, String, Text)
from sqlalchemy.orm import backref, relation
from database import Base, engine

import pandas as pd
from enum import Enum, auto
from datetime import datetime as dt


def dropTable(name):
    cursor = engine.connect()
    stmt = "DROP table "+name
    cursor.execute(stmt)

class UserRole(Enum):
    ADMIN = auto()
    AUTHOR = auto()
    DEFAULT = auto()

    @staticmethod
    def members():
        return UserRole._member_names_


class Users(Base):
    __tablename__ = "Users"
    id = Column("user_id", Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(100), unique=True)
    func = Column(String(200))
    pwd = Column(String(132))
    salt = Column(String(32), nullable=True)
    created = Column(DateTime, nullable=True,server_default=str(dt.now()))
    role = Column(String(32), nullable=True)
#    updated = Column(DateTime(timezone=True), onupdate=dt.now().isoformat())

    def __init__(self, name, email, func, pwd, salt=None, role: UserRole = None):
        self.name = name
        self.email = email
        self.func = func
        self.pwd = pwd
        self.role = role
        if salt is not None:
            salt = salt
        else:
            self.salt = self.pwd.split("$")[1]
        self.created = None

    def __repr__(self):
        return f"<User {self.name} with id {self.id}>"


class Location(Base):
    __tablename__ = "Location"
    id = Column("locationID", Integer, primary_key=True)
    name = Column(String(256))
    #x = Column(Float(8))
    #y = Column(Float(8))
    streetname = Column(String(256))
    streetnumber = Column(String(128))
    city = Column(String(256))
    country = Column(String(32))
    foreign = relation('Event', backref=backref('Location'))

    def __init__(self, name: str, streetname: str, streetnumber: str, city: str, country: str):
        self.name = name
        self.streetname = streetname
        self.streetnumber = streetnumber
        self.city = city
        self.country = country


class EventType(Enum):
    CLUB = auto()
    OUTDOOR = auto()
    FESTIVAL = auto()
    BEACH = auto()
    FOREST = auto()


class Event(Base):
    __tablename__ = "Event"
    id = Column("EventID", Integer, primary_key=True, autoincrement=True)
    name = Column(String(120))
    eventdate = Column(DateTime,nullable=True)
    #eventstarttime = Column(Integer)
    #date = Column(String(64),DateTime)
    #time = Column(Time(timezone=True))
    location = Column(String(256), ForeignKey('Location.name'))
    organizer = Column(String(120), nullable=True)
    description = Column(Text(), nullable=True)
    price = Column(Integer, nullable=True)
    maxtickets = Column(Integer, nullable=True)
    eventtype = Column(String(32))
#    Created = Column(DateTime(timezone=True), server_default=func.now())
#    LastUpdate = Column(DateTime(timezone=True), onupdate=dt.now())

    """Create an event and publish tickets for it"""

    def __init__(self, name: str, eventdate, location: Location, price: str, eventtype: EventType, organizer=None, image=None, maxtickets=10, description=None):
        self.name = name
        self.location = location
        self.eventdate = eventdate
        self.price = price
        self.maxtickets = maxtickets
        self.organizer = organizer
        if image is not None:
            self.Image = image
        else:
            self.Image = "https://persgroep.pubble.cloud/d9c7ad83/content/2019/3/151e47b4-5655-43cf-b37b-40edd2e8b6e3_thumb840.jpg",

        self.eventtype = eventtype
        self.description = description
        #self.json = json.dumps(self, indent=4, skipkeys=True)


class Organizer:
    pass


class Ticket:
    pass
