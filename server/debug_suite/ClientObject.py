import requests
import html5lib
from bs4 import BeautifulSoup as bs4
import lxml

class TestPlayer(object):
    """Class for creating mock players for automated server tester."""
    def __init__(self, name, hitServer=False):
        self.name = name
        self.id = None
        self.ids = None
        if hitServer:
            print("to server")
            self.base = 'https://secret-ravine-44641.herokuapp.com/sh/'
        else:
            print('not to server')
            self.base = "http://127.0.0.1:8000/sh/"

    def client_call_for_http(self, uri):
        x = requests.get(self.base + uri).text
        y = bs4(x, "lxml")
        y = y.body.p.text
        return y

    def client_call_for_json(self, uri):
        x = requests.get(self.base + uri)
        # print(x, type(x))
        try:
            return x.json()
        except:
            print(x)
            raise ValueError('Something went wrong with the {0} request.'.format(uri))

    def dryCall(self, uri):
        requests.get(self.base + uri)
        return


# https://secret-ravine-44641.herokuapp.com/sh/
# http://127.0.0.1:8000/sh/