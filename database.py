from sqlalchemy import create_engine, Column, Integer, DateTime, ForeignKey, MetaData, func
from sqlalchemy.orm import scoped_session, sessionmaker, registry, declared_attr
from datetime import datetime as dt
from config import DB_PATH
from typing import Any

from dataclasses import dataclass, field

# Notes on further database development: https://www.example.com


class RaveDB:
    def __init__(self, db_path):
        self.engine = create_engine(db_path)
        self.metadata = MetaData(self.engine)
        self.table_names = self.engine.table_names()
        self.sorted_tables = self.metadata.sorted_tables
        self.mapper_registry = registry(metadata=self.metadata)
        self.schema = self.metadata.schema

    def sessionmaker(self,  autocommit=False, autoflush=False):
        return sessionmaker(autocommit=autocommit,
                            autoflush=autoflush, bind=self.engine)

    def init_db(self):
        return self.metadata.create_all()

    def configure(self):
        return self.mapper_registry.configure()


db = RaveDB("sqlite:///"+DB_PATH)
sesh = scoped_session(db.sessionmaker())


@db.mapper_registry.as_declarative_base()
class Base(object):
    """Defines a declarative model for all tables"""
    id = Column(Integer, primary_key=True)

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    created = Column(DateTime, default=func.now())

    updated = Column(DateTime, onupdate=func.now(),
                     nullable=True)

    query = sesh.query_property()

    @declared_attr
    def __items__(cls):
        return cls.__dict__.items()

    @declared_attr
    def __repr__(cls) -> str:
        return f"<{cls.id} {cls.name}> "

    @classmethod
    @declared_attr
    def headers(cls) -> list:
        return [c for c in cls.__table__.columns.keys()]
