from django.test import TestCase

from .models import Player, GameState, Voting, PolicyDeck, DiscardPile, PresidentQueue
from .views import *

import requests
import json

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