#!/usr/bin/python3

from ClientObject import TestPlayer

import sys
import json
import time
import requests
from bs4 import BeautifulSoup as bs# Beautiful Soup 4
import lxml
import pprint

def standard5Player(hold=False):
    a = TestPlayer('a')
    b = TestPlayer('b')
    c = TestPlayer('c')
    d = TestPlayer('d')
    e = TestPlayer('e')

    # a is the host. Calls to start the game.
    try:
        '''At this point, the server doesn't actually send any form of response.
        It enters a while loop in the start() view while it waits for the
        previously listed number of players to join. Requests will wait 
        indefinitely if no response is received and throws a
        script-crashing error if the timeout option is used to bypass this
        functionality. The only solution I could think of was to catch the
        exception and move on. This requires immediate remedy...'''
        checkServerOn = requests.get('http://127.0.0.1:8000/sh/setup/1/5', timeout=4)
        # TODO (1) Find a better way to handle this request.
    except:
        pass
    # waitForIt(hold)
    a.id = int(a.client_call_for_http('client/join_game/' + a.name))
    a.ids = str(a.id)
    waitForIt(hold)
    b.id = int(b.client_call_for_http('client/join_game/' + b.name))
    b.ids = str(b.id)
    waitForIt(hold)
    c.id = int(c.client_call_for_http('client/join_game/' + c.name))
    c.ids = str(c.id)
    waitForIt(hold)
    d.id = int(d.client_call_for_http('client/join_game/' + d.name))
    d.ids = str(d.id)
    waitForIt(hold)
    e.id = int(e.client_call_for_http('client/join_game/' + e.name))
    e.ids = str(e.id)
    waitForIt(hold)

    # a should be president now
    time.sleep(10)
    checkSelectionJson = a.client_call_for_json('client/nominate_chancellor/' + str(a.id))
    if type(checkSelectionJson) != type({}):
        print(type(checkSelectionJson))
        raise ValueError("something wrong with president nominateChancellor view:")
    waitForIt(hold)

    # a nominates b for chancellor
    checkNominateChancellorResponse = a.client_call_for_json('client/nominate_chancellor/{0}'.format(str(a.id)))
    pprint.pprint(checkNominateChancellorResponse)
    if not quickCheck(checkNominateChancellorResponse, "b"):
        print("Error inbound. JSON data received:\n" + str(checkNominateChancellorResponse))
        raise AssertionError("b was not added to the response JSON for client/nominate_chancellor")
    waitForIt(hold)
    checkServerOn = a.client_call_for_http('client/nominate_chancellor_order/{0}/{1}'.format(str(a.id), str(b.id)))
    if checkServerOn != "confirm":
        raise AssertionError("did not receive confirmation from nominate_chancellor_order")

    # make sure everyone receives correct president/chancellor election information    
    checkVoteInfo = e.client_call_for_http('client/heads_up')
    if checkVoteInfo != "President a has nominated b to server as their Chancellor.":
        print("Error coming: info received for P/C election pairing: " + checkVoteInfo)
        raise(AssertionError("text not processing correctly, headsUpToVote"))

    # All yas
    waitForIt(hold)
    """The aGot call was originally positioned here. For some reason, the server
    would get the Http request, response with confirmation, create the Voting vote
    object, but it would not appear in the database. all other requests worked after
    putting in time between votes but a's call did not. Moving it to the bottom
    seems to have helped, but there may be an issue with client calls coming to
    close together."""
    waitForIt(hold)
    bGot = b.client_call_for_http('client/submit_vote/{0}/{1}'.format(str(b.id), "1"))
    waitForIt(hold)
    cGot = c.client_call_for_http('client/submit_vote/{0}/{1}'.format(str(c.id), "1"))
    waitForIt(hold)
    dGot = d.client_call_for_http('client/submit_vote/{0}/{1}'.format(str(d.id), "1"))
    waitForIt(hold)
    eGot = e.client_call_for_http('client/submit_vote/{0}/{1}'.format(str(e.id), "1"))
    waitForIt(hold)
    aGot = a.client_call_for_http('client/submit_vote/{0}/{1}'.format(str(a.id), "1"))
    waitForIt(hold)
    for i in [aGot, bGot, cGot, dGot, eGot]:
        print(i)
        if i != 'confirm':
            raise AssertionError("something went wrong in vote, submit_vote, or Voting db")

    # wait a sec, confirm GameState.statusID is 9 for policy action. 
    # confirm president, chancellor assigned
    waitForIt(hold)
    checkServerOn = a.client_call_for_json('client/client_status/{0}'.format(str(a.id)))
    if checkServerOn["statusID"] != 9:
        raise AssertionError("statusID not set to appropriate value.")


    # a draws policy cards (will attempt to discard a Fascist policy if one is present).
    presidentCards = a.client_call_for_json(f'client/president_draw/{a.ids}')
    waitForIt(hold)
    toDiscard = None
    toPass = []
    for i in presidentCards:
        if presidentCards[i] == "Fascist" and toDiscard == None:
            toDiscard = presidentCards[i]
        else:
            toPass.append(presidentCards[i])
    print(toPass, toDiscard)
    checkServerOn = a.client_call_for_http(f'client/president_play/{toPass[0]}/{toPass[1]}/{toDiscard}')

    # cards pass to b. b chooses a policy card to play (will attempt to play a Liberal card if one is present)
    waitForIt(hold)
    checkServerOn = a.client_call_for_json('client/client_status/{0}'.format(str(a.id)))
    if checkServerOn["statusID"] != 10:
        raise AssertionError("statusID not set to appropriate value.")
    chancellorCards = b.client_call_for_json(f'client/chancellor_draw/{b.ids}')
    waitForIt(hold)
    if chancellorCards["0"] == "Liberal":
        b.client_call_for_http(f'client/chancellor_play/0/1')
    else:
        b.client_call_for_http(f'client/chancellor_play/1/0')
    return

""" TODO (1) the automation suite is intended to help debug server interaction
and functionality. Before thinking to automate these task, I had to manually
visit each client-facing url with the data necessary to confirm that the 
server is functioning and running as intended. A much easiest solution is to
script through various scenerios that allow for the same type of thorough testing
but in a fraction of the time. This suite, though not officially a unit test or 
test module, can also be run after refactors/changes to server to assure the
server maintains functionality without regession. To be able to effectively
automate a selection of scenarios toward this psuedo-testing end, I require
the ability to create mock data (i.e. feed specific information to the server 
databases). Attempt to write a workout/testing mode setting to views.py that
will allow for test db creation and manipulation."""


    
def quickCheck(dictionary, valueTarget):
    for i in dictionary:
        if dictionary[i] == valueTarget:
            return True
    return False

def waitForIt(doWait):
    if doWait:
        x = input('')
        return
    else:
        time.sleep(2)
        return

if __name__ == '__main__':
    if "hold" not in sys.argv:
        standard5Player()
    else:
        standard5Player(True)