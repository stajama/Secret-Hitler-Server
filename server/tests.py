from django.test import TestCase

from .models import Player, GameState, Voting, PolicyDeck, DiscardPile, PresidentQueue
from .views import *

import requests
import json
import random

class testing(TestCase):

    def setUp(self):
        clearAll()

    def tearDown(self):
        clearAll()

    def test_cyclePresident(self):
        """cyclePresident() is a helper function that takes the current next
        in line player in the PresidentQueue, sets there president value to
        True, and adds them to the end of the queue. If the entry has the
        special (for Special Election) value set to true, it should not add
        that entry to the end of the queue again."""
        fivePlayerSetup()
        for i in Player.objects.all():
            x = PresidentQueue(playerID=i.id)
            x.save()
        PQ = PresidentQueue.objects.all()
        self.assertEqual(len(PQ), 5)
        cyclePresident()
        PQ = PresidentQueue.objects.all()
        self.assertEqual(len(PQ), 5)
        PQ = PresidentQueue.objects.all()
        self.assertEqual(PQ[0].playerID, Player.objects.get(name='test1').id)
        insertPresident(PQ[4].playerID)
        PQ = PresidentQueue.objects.all()        
        self.assertEqual(len(PQ), 6)
        self.assertEqual(PQ[0].playerID, Player.objects.get(name='test0').id)
        self.assertEqual(PQ[1].playerID, Player.objects.get(name='test1').id)
        cyclePresident()
        PQ = PresidentQueue.objects.all()
        self.assertEqual(len(PQ), 5)
        self.assertEqual(PQ[0].playerID, Player.objects.get(name='test1').id)
        cyclePresident()
        PQ = PresidentQueue.objects.all()
        self.assertEqual(len(PQ), 5)
        self.assertEqual(PQ[0].playerID, Player.objects.get(name='test2').id)
        cyclePresident()
        PQ = PresidentQueue.objects.all()
        self.assertEqual(len(PQ), 5)
        self.assertEqual(PQ[0].playerID, Player.objects.get(name='test3').id)
        cyclePresident()
        PQ = PresidentQueue.objects.all()
        self.assertEqual(len(PQ), 5)
        self.assertEqual(PQ[0].playerID, Player.objects.get(name='test4').id)
        cyclePresident()
        PQ = PresidentQueue.objects.all()
        self.assertEqual(len(PQ), 5)
        self.assertEqual(PQ[0].playerID, Player.objects.get(name='test0').id)
        clearAll()

    def test_drawCard(self):
        """drawCard() is a helper function that allows one-point access to
        draw a card from the Policy Deck (either for the President during
        policy handling or through a forced policy via the election tracker).
        Simply draws the top card from the deck and returns the value of the card."""
        pass
        setUpPolicyDeck()
        self.assertEqual(len(PolicyDeck.objects.all()), 17)
        hold = []
        for i in range(17):
            hold.append(drawCard())
        self.assertEqual(len(PolicyDeck.objects.all()), 0)
        self.assertEqual(hold.count('Liberal'), 6)
        self.assertEqual(hold.count('Fascist'), 11)
        clearAll()

    def test_cleanSpaces(self):
        self.assertEqual(cleanSpaces("t_e_s_t"), "t e s t")
        self.assertEqual(cleanSpaces("test"), "test")
        self.assertEqual(cleanSpaces("Jim_Bob"), "Jim Bob")
        return

    def test_getStatus(self):
        clearAll()
        fivePlayerSetup1()
        P = Player.objects.all()
        self.assertEqual(getStatus(P[0].id), {"livingPlayerCount": 5,
                                              "id": P[0].id,
                                              "name": "test0",
                                              "party": "Liberal",
                                              "role": "Liberal",
                                              "alive": True,
                                              "statusID": 3,
                                              "statusUpdate": "The current President is test0. Waiting for the President to nominate a Chancellor.",
                                              "fasPolicies": 0,
                                              "libPolicies": 0,
                                              "electionTracker": 0})
        self.assertEqual(getStatus(P[1].id), {"livingPlayerCount": 5,
                                              "id": P[1].id,
                                              "name": "test1",
                                              "party": "Liberal",
                                              "role": "Liberal",
                                              "alive": True,
                                              "statusID": 3,
                                              "statusUpdate": "The current President is test0. Waiting for the President to nominate a Chancellor.",
                                              "fasPolicies": 0,
                                              "libPolicies": 0,
                                              "electionTracker": 0})        
        self.assertEqual(getStatus(P[2].id), {"livingPlayerCount": 5,
                                              "id": P[2].id,
                                              "name": "test2",
                                              "party": "Liberal",
                                              "role": "Liberal",
                                              "alive": True,
                                              "statusID": 3,
                                              "statusUpdate": "The current President is test0. Waiting for the President to nominate a Chancellor.",
                                              "fasPolicies": 0,
                                              "libPolicies": 0,
                                              "electionTracker": 0})
        self.assertEqual(getStatus(P[3].id), {"livingPlayerCount": 5,
                                              "id": P[3].id,
                                              "name": "test3",
                                              "party": "Fascist",
                                              "role": "Fascist",
                                              "alive": True,
                                              "statusID": 3,
                                              "statusUpdate": "The current President is test0. Waiting for the President to nominate a Chancellor.",
                                              "fasPolicies": 0,
                                              "libPolicies": 0,
                                              "electionTracker": 0,
                                              "Other Fascists": "",
                                              "Hitler": "test4"})
        self.assertEqual(getStatus(P[4].id), {"livingPlayerCount": 5,
                                              "id": P[4].id,
                                              "name": "test4",
                                              "party": "Fascist",
                                              "role": "Hitler",
                                              "alive": True,
                                              "statusID": 3,
                                              "statusUpdate": "The current President is test0. Waiting for the President to nominate a Chancellor.",
                                              "fasPolicies": 0,
                                              "libPolicies": 0,
                                              "electionTracker": 0,
                                              "Other Fascists": "test3"})
        clearAll()
        return

    def test_votingMachine(self):
        clearAll()
        fivePlayerSetup1()
        for i in Player.objects.all():
            V = Voting(name=i.name, vote=True)
            V.save()
        G = GameState.objects.all()[0]
        G.statusID = 99
        G.save()
        self.assertEqual(votingMachine(), {"number of votes": 5,
                                           "test0": True,
                                           "test1": True,
                                           "test2": True,
                                           "test3": True,
                                           "test4": True,
                                           "result": "The vote passed."})
        Voting.objects.all().delete();
        for i in Player.objects.all():
            V = Voting(name=i.name, vote=False)
            V.save()
        G = GameState.objects.all()[0]
        G.statusID = 98
        G.save()
        self.assertEqual(votingMachine(), {"number of votes": 5,
                                           "test0": False,
                                           "test1": False,
                                           "test2": False,
                                           "test3": False,
                                           "test4": False,
                                           "result": "The vote failed. Citizen frustration will increase."})
        Voting.objects.all().delete();
        for i in Player.objects.all():
            if i.name != "test3" and i.name != "test4":
                V = Voting(name=i.name, vote=False)
                V.save()
            else:
                V = Voting(name=i.name, vote=True)
                V.save()
        G = GameState.objects.all()[0]
        G.statusID = 98
        G.save()
        self.assertEqual(votingMachine(), {"number of votes": 5,
                                           "test0": False,
                                           "test1": False,
                                           "test2": False,
                                           "test3": True,
                                           "test4": True,
                                           "result": "The vote failed. Citizen frustration will increase."})
        clearAll()
        return

    def test_votingTally(self):
        clearAll()
        fivePlayerSetup()
        mockInput = {"1": True, "2": True, "3": True, "4": True, "5": True}
        for i in mockInput:
            V = Voting(name=i, vote=mockInput[i])
            V.save()
        self.assertEqual(votingTally(), True)
        Voting.objects.all().delete();
        mockInput = {"1": True, "2": True, "3": True, "4": True, "5": False}
        for i in mockInput:
            V = Voting(name=i, vote=mockInput[i])
            V.save()
        self.assertEqual(votingTally(), True)  
        Voting.objects.all().delete();
        mockInput = {"1": True, "2": True, "3": True, "4": False, "5": False}
        for i in mockInput:
            V = Voting(name=i, vote=mockInput[i])
            V.save()
        self.assertEqual(votingTally(), True)  
        Voting.objects.all().delete();
        mockInput = {"1": True, "2": True, "3": False, "4": False, "5": False}
        for i in mockInput:
            V = Voting(name=i, vote=mockInput[i])
            V.save()
        self.assertEqual(votingTally(), False)
        clearAll()
        return

    def test_getLivingCount(self):
        clearAll()
        fivePlayerSetup1()
        self.assertEqual(getLivingCount(), 5)
        P = Player.objects.all()[0]
        P.isAlive = False
        P.save()
        self.assertEqual(getLivingCount(), 4)
        P = Player.objects.all()[1]
        P.isAlive = False
        P.save()
        self.assertEqual(getLivingCount(), 3)
        P = Player.objects.all()[2]
        P.isAlive = False
        P.save()
        self.assertEqual(getLivingCount(), 2)
        P = Player.objects.all()[3]
        P.isAlive = False
        P.save()
        self.assertEqual(getLivingCount(), 1)
        P = Player.objects.all()[4]
        P.isAlive = False
        P.save()
        self.assertEqual(getLivingCount(), 0)
        clearAll()
        return

    def test_checkCurrentVotes(self):
        clearAll()
        correctList = []
        for i in range(10):
            V = Voting(name=f"test{str(i)}", vote=[True, False][random.randint(0, 1)])
            V.save()
            correctList.append(f"test{str(i)}")
            self.assertEqual(checkCurrentVotes(), correctList)
        clearAll()
        return

    def test_findCurrentPresident(self):
        '''Currently, it is impossible to test findCurrentPresident() properly.
        Much of the logic tied to assigning and cycling presidents is tied to
        situational cues (if a vote passes/fails, etc.). In the future, this
        functionality should be decoupled and separated to allow for proper
        testing.'''
        return


def fivePlayerSetup(num=5):
    G = GameState(numberOfPlayers=num)
    G.save()
    for i in range(num):
        x = Player(name="test" + str(i))
        x.save()
    setUpMatch()
    return

def clearAll():
    Player.objects.all().delete()
    GameState.objects.all().delete()
    Voting.objects.all().delete()
    PolicyDeck.objects.all().delete()
    DiscardPile.objects.all().delete()
    PresidentQueue.objects.all().delete()
    return

def printAll():
    PQ = PresidentQueue.objects.all()
    for i in PQ:
        print(i.playerID, i.special)

def fivePlayerSetup1(num=5):
    G = GameState(numberOfPlayers=num)
    G.save()
    for i in range(num):
        x = Player(name="test" + str(i))
        x.save()
    finalizeResources()
    P = Player.objects.all()[0];
    P.role = "Liberal"
    P.party = "Liberal"
    P.save()
    P = Player.objects.all()[1];
    P.role = "Liberal"
    P.party = "Liberal"
    P.save()
    P = Player.objects.all()[2];
    P.role = "Liberal"
    P.party = "Liberal"
    P.save()
    P = Player.objects.all()[3];
    P.role = "Fascist"
    P.party = "Fascist"
    P.save()
    P = Player.objects.all()[4];
    P.role = "Hitler"
    P.party = "Fascist"
    P.save()
    return