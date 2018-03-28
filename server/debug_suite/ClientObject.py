import requests
import html5lib
from bs4 import BeautifulSoup as bs4
import lxml

class TestPlayer(object):
    """Class for creating mock players for automated server tester."""
    def __init__(self, name):
        self.name = name
        self.id = None
        self.ids = None

    def client_call_for_http(self, uri):
        x = requests.get('http://127.0.0.1:8000/sh/' + uri).text
        y = bs4(x, "lxml")
        y = y.body.p.text
        return y

    def client_call_for_json(self, uri):
        x = requests.get('http://127.0.0.1:8000/sh/' + uri)
        # print(x, type(x))
        try:
            return x.json()
        except:
            print(x)
            raise ValueError('Something went wrong with the {0} request.'.format(uri))

