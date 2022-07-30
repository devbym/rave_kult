# -*- coding: utf-8 -*-


### TELEGRAM CONFIGURATION ###
from json import load


with open("/home/m/Documents/Dev/BOTS/sleutels.json","r",encoding='utf-8') as keyfile:
  keys = load(keyfile)

TOKEN = keys.get('Telegram')['KEY']

TIMEZONE = 'Europe/Amsterdam'
TIMEZONE_COMMON_NAME = 'Amsterdam'
VERSION = "0.1"
COUNTRIES = ["CZ","SK","DE","NL","BE"]
REMOTE_EVENT_FILE_URL = "https://raw.githubusercontent.com/devbym/devbym_rave_bot/main/events.json"

