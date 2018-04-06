#!/usr/bin/python3

from ClientObject import TestPlayer

import sys
import json
import time
import requests
from bs4 import BeautifulSoup as bs# Beautiful Soup 4
import lxml
import pprint

def appMockUpTest1():
    """app is running on phone. This function makes 4 additional calls to /client/join_game
    to simulate other players online."""
    a = TestPlayer('a')
    for i in range(4):
        a.client_call_for_http('client/join_game/player' + str(i))
    return True

if __name__ == '__main__':
    appMockUpTest1()