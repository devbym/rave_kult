from database import db
from geopy.geocoders import Nominatim
from typing import Iterable, List
import logging
import json


UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:103.0) Gecko/20100101 Firefox/103.0"


class DataController():
    @staticmethod
    def x(statement):
        with db.engine.connect() as conn:
            result = conn.execute(statement)
            return [row for row in result]

    @staticmethod
    def select(table: str, columns: List[str]):
        columns = ' , '.join(columns)
        statement = f"SELECT {columns} FROM {table}"
        data = DataController.x(statement)
        return data

    @staticmethod
    def insert(table: str, columns: Iterable, values: Iterable):
        if len(columns) == len(values):
            statement = f"INSERT INTO {table} COLUMNS {columns} VALUES ({values})"
            data = DataController.x(statement)
            return data
        else:
            raise ValueError(
                "Length of [columns] and [values] should be equal")

    @staticmethod
    def drop(table):
        """Can be called before DB initialisation to drop a table """
        statement = f"DROP TABLE {table} IF EXISTS"
        data = DataController.x(statement)
        return data


class AddressMeta():
    def __init__(self, data: dict):
        self.street = data.get('road')
        self.number = data.get('house_number')
        self.postcode = data.get('postcode')
        self.suburb = data.get('suburb')
        self.city = data.get('city')
        self.country = data.get("country")
        # self.country = Country(data.get('country'),data.get("country-code"))

    def __repr__(self) -> str:
        return f"{self.street} {self.number}\n{self.postcode} {self.city}\n{self.country}"


class Geo:
    # We can adapt the UA string later with the one from the user itself
    def __init__(self, x: float, y: float, geoloc=Nominatim(user_agent=UA)) -> None:
        self.x = x
        self.y = y
        self.location = geoloc.reverse(
            f"{str(self.x)},{str(self.y)}", language="en")
        self.raw = self.location.raw
        self.address = self.location.address
        self.lat = self.location.latitude
        self.lon = self.location.longitude
        self.coords = (self.x, self.y)

    def __repr__(self) -> str:
        return f"< [X:{self.x}, Y:{self.y}] @ {self.location.address}>"

    def getAddress(self) -> dict:
        new = AddressMeta(self.raw['address'])
        return new  # dict(self.raw['address'])


class C2():
    def __init__(self, name: str, code: str, cities=[], **kwargs) -> dict:
        self.name: str = name
        self.code: str = code
        self.cities: list = cities

    def __repr__(self):
        return self.code


class CountryCode:
    def __init__(self, countryname: str):
        with open("static/country_abbreviations.json", "r", encoding="utf-8") as abv:
            data = json.load(abv)
            countries = data
            for ctr in countries:
                if ctr['Name'] == countryname:
                    self.code = ctr['Code']

    def __repr__(self):
        return self.code


def updateCities(countryName):
    ctr = Country.query.filter_by(name=countryName).first()
    if not ctr.cities:
        with open("static/cities.json", "r", encoding="utf-8") as fp:
            data = json.load(fp)
            res = data.get("Europe")[countryName]
            print(res)
            return res
    return


def getCountries(continent: str, path="static/countries.json"):
    with open(path, "r", encoding='utf-8') as fo:
        pre: dict = json.load(fo)
        c = dict()
        for k, v in pre.get(continent).items():
            cities = v.get('cities')
            if cities:
                c2 = C2(k, v.get('code'), cities=cities)
            c.update({k: c2})
        return c


def rmvBadges():
    bd = Badge.query.all()
    bds = []
    for x in bd:
        print(x)
        if x.name not in bds:
            bds += [x.name]
        else:
            sesh.delete(x)
    sesh.commit()
    return Badge.query.all()
