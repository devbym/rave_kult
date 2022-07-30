import json ,calendar
from datetime import datetime as dt
from enum import Enum

MONTHS = [x for x in calendar.month_name if x != '']

cal = calendar.Calendar.yeardatescalendar(2022,width=1)


class Events:
    @staticmethod
    def load_year(year,month=None):
        with open("events.json",mode="r",encoding="utf-8") as fo:
            fd = json.load(fo)
            events = fd['events'][str(year)]
        if month is not None:
            mon = dict()
            name= MONTHS.index(month)
            mon[name] = events[str(month)]
            return mon
        return events

    @staticmethod
    def load_month(year,month):
        mon = dict()
        with open("events.json",mode="r",encoding="utf-8") as fo:
            fd = json.load(fo)
            events = fd['events'][str(year)]

            return mon

    def add(event):
        pass


class Event:
    eventdate = dt()
    day = ''
    def __init__(self,location,venue,eventdate,starttime) -> None:
        self.location = location
        self.venue = venue
        super().__init__()




EVENTS = Events.load_year(2022)

