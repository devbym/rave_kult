from dataclasses import dataclass, field
from typing import List
import logging as log
from flask_sqlalchemy import Model

from sqlalchemy import (Column, DateTime,
                        ForeignKey, Integer, String, Text, Float)
from sqlalchemy.orm import backref, relation, column_property

from database import Base, sesh, db
from enum import Enum, auto
from werkzeug.security import check_password_hash
from datetime import datetime as dt


class EventType(Enum):
    CLUB = auto()
    OUTDOOR = auto()
    FESTIVAL = auto()
    BEACH = auto()
    FOREST = auto()
    SECRET = auto()
    OTHER = auto()
    BUSINESS = auto()


class Event(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    date = Column(String(120), nullable=False)
    duration = Column(Integer)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=True)
    maxtickets = Column(Integer, nullable=True)
    type = Column(String(32), default=str(EventType.CLUB))
    badges = relation("Badge", backref=backref('event'))

    location = Column(
        String, ForeignKey('location.name'), nullable=False)
    org = Column(Integer, ForeignKey('organisation.id'), nullable=False)
    city = Column(Integer, ForeignKey('city.id'), nullable=False)
    banner = Column(Integer, ForeignKey('eventimage.id'), nullable=False)

    """Add an init function? Or use dataclasses to defer an init method. Dataclasses must be integrated with SQLalchemy """

    def __repr__(self):
        return f"<{self.id}: EVENT {self.name} in {self.location} by: {self.org} on {self.date}>"

    @classmethod
    def row(self):
        return sesh.scalars(select(self))

    @classmethod
    def getAll(cls):
        return {event for event in cls.query.all()}

    @staticmethod
    def add(r: dict, **kwargs):
        ev = Event(
            name=r.get("eventname"),
            date=r.get("eventdate"),
            duration=r.get("eventduration"),
            location=r.get("eventlocation"),
            description=r.get("eventdescription"),
            price=r.get("eventprice"),
            type=r.get("eventtype"),
            org=r.get("eventorg"),
            city=r.get("eventcity"),
            banner=r.get("eventbanner")
        )

        # ev.badges.append(["SOLD OUT"])
        return ev


class UserRole(Enum):
    ADMIN = auto()
    AUTHOR = auto()
    USER = auto()
    DEFAULT = auto()

    def __repr__(self) -> str:
        return super().__repr__()

    @ staticmethod
    def members():
        return UserRole.__members__


@db.mapper_registry.mapped
@dataclass
class Location:
    __tablename__ = "location"
    __sa_dataclass_metadata_key__ = "sa"
    id: int = field(init=False, metadata={
        "sa": Column(Integer, primary_key=True)})
    name: str = field(default=None, metadata={
        "sa": Column(String(50), unique=True)})
    x: float = field(default=False, metadata={
        "sa":    Column(Float)
    })
    y: float = field(default=False, metadata={
        "sa":    Column(Float)
    })
    streetname = Column(String(256))
    streetnumber = Column(String(128))
    city: int = field(default=False, metadata={
        "sa": Column(Integer, ForeignKey("city.id"), nullable=False)
    })
    country: str = field(default=False, metadata={"sa": Column(
        String, ForeignKey("country.name"), nullable=False)})
    # country_id: int = field(default=False, metadata={
    #     "sa": Column(Integer, ForeignKey('country.id'))})

    query = sesh.query_property()


class Country(Base):
    """ Defines a Country with its countrycode"""
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    code = Column(String(5), nullable=False)
    cities = relation("City", backref=backref('country'), lazy="subquery")
    # locations = relation("Location", lazy=True)

    def __repr__(self):
        return f'<{self.name}>'


@db.mapper_registry.mapped
@dataclass
class Stad:
    __tablename__ = "stad"
    __sa_dataclass_metadata_key__ = "sa"
    id: int = field(init=False, metadata={
        "sa": Column(Integer, primary_key=True)})
    name: str = field(default=None, metadata={
        "sa": Column(String(50), unique=True)})
    country: str = field(default=None, metadata={"sa": Column(
        String, ForeignKey("country.name"), nullable=False)})


class City(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    organisations = relation('Organisation')
    country_id = Column(Integer, ForeignKey('country.id'), nullable=False)

    def __init__(self, name: str, country: Country) -> None:
        self.name = name
        self.country = country

    def __repr__(self):
        return f'<{self.name}, {self.country.code}>'


class Users(Base):
    email = Column(String(100), unique=True)
    func = Column(String(200))
    pwd = Column(String(132))
    salt = Column(String(32), nullable=True)
    role = Column(String(32), nullable=True)

    def __init__(self, name, email, func, pwd, role: UserRole, **salt):
        self.name = name
        self.email = email
        self.func = func
        self.pwd = pwd
        self.role = str(role)
        if salt is not None:
            salt = salt
        else:
            self.salt = self.pwd.split("$")[1]

    def __repr__(self):
        return f"<User {self.name}:Id {self.id}>"

    @ staticmethod
    def getAll():
        return {event for event in sesh.query(Users).all()}

    @ staticmethod
    def login(request):
        r = request.form
        user = Users.query.filter(Users.name == r.get("name")).first()
        check = check_password_hash(user.pwd, r.get("pwd"))
        if user:
            if check:
                log.info("Login successful")
                return user
            elif not check:
                log.info("Password incorrect")
                return None
        else:
            msg = (f"User {r.get('name')} not found. \n")
            raise UserWarning.args+msg


class Organisation(Base):
    def __init__(self, name: str, country: str, city: str, url=None) -> None:
        self.name = name
        self.country = country
        self.city = city
        self.url = url
    name = Column(String(256), nullable=False)
    country = Column(String, ForeignKey("country.name"),
                     nullable=False)  # One-to-many
    city = Column(String, ForeignKey("city.name"), nullable=False)
    url = Column(String, nullable=True)
    events = relation("Event", backref=backref(
        'organisation'), lazy='subquery')

    def __repr__(self) -> str:
        return f"<ORG:{self.name} ID: {self.id} COUNTRY: {self.country}>"


class EventImage(Base):
    id = Column(Integer, primary_key=True)
    # event = Column(String, ForeignKey('event.id'), nullable=False)
    src = Column(String(256))
    data = Column(Text)
    image = relation("Event", backref=backref('images', lazy='subquery'))

    def __repr__(self):
        return f"<EVENT:{self.event} - SRC:{self.src}>"


class Badge(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    icon = Column(String, nullable=True)
    event_id = Column(Integer, ForeignKey("event.id"))
    # event = relation("Event", backref=backref('badges', lazy='joined'))

    def __repr__(self) -> str:
        return f"<{self.id} {self.name} {self.icon}>"


Country.orgs = relation(
    "Organisation")
#Country.locations = relation("Location")
# Country.locations = relation("location", lazy="subquery")


# Organisation.events = relation("Event",backref=backref('organized',lazy='subquery'))
# City.events = relation("Event",backref=backref('city',lazy=True))
Location.events: List[Event] = field(default_factory=list, metadata={
    "sa": relation("Event", backref=backref('location'))})

# MIXINS


class Post(Model):
    id = Column(Integer, primary_key=True)
    title = Column(String(80), nullable=False)
    body = Column(Text, nullable=False)
    pub_date = Column(DateTime, nullable=False, default=dt.utcnow)

    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    category = relation('Category', backref=backref('posts', lazy=True))

    def __repr__(self):
        return f'<Post {self.title}>'


class Category(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)

    def __repr__(self):
        return f'<Category {self.name}>'


# rave = Category(name="RAVE")
# Post(title="abc",body="Some text here",category=rave)
# Post(title="xyz",body="ZYV text here",category=rave)
# xpost = Post(title=ev.name,body=ev.description)
# rave.posts.append(xpost)
# sesh.add(rave)
# print(rave.posts,xpost.category)

class File(Base):
    __tablename__ = 'file'

    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    extension = Column(String(8))
    filename = column_property(name + '.' + extension)
    path = column_property('C:/' + filename.expression)


class Ticket:
    pass

# q = sesh.query(File.path).filter(File.filename == 'foo.txt')
