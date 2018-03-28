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

    def test_views_findCurrentPresident(self):
        """findCurrentPresident() is used as a quick helper function to pull
        the current presidents Player database information. Allows quick
        access to president's name and id as well as easy identify verification
        to prevent bugs or access to president only views by non-presidents."""

        fivePlayerSetup()
        P = Player.objects.all()
        example = Player.objects.get(pk=P[0].id)
        example.president = True
        example.save()
        self.assertEqual(findCurrentPresident(), P[0])
        example = Player.objects.get(pk=P[1].id)
        example.president = True
        example.save()
        with self.assertRaises(AssertionError):
            findCurrentPresident()
        example.president = False
        example.save()
        example = Player.objects.get(pk=P[0].id)
        example.president = False
        example.save()
        with self.assertRaises(ValueError):
            findCurrentPresident()

        """post function: the post function was added and a later refactor.
        The president's role is changed immediately after a successful election
        to previousPresident. This makes it easier to track term-limited 
        layers while keeping the current President status clean for possible
        failed elections. The problem presented is that post-election, all
        findCurrentPresident checks require the previousPresident, not the
        current President (whomever happens to be at the top of the PresidentQueue)."""
        example.president = True
        example.save()
        self.assertEqual(findCurrentPresident(), P[0])
        example.previousPresident = True
        example.president = False
        example.save()
        example = Player.objects.get(pk=P[1].id)
        example.president = True
        example.save()
        self.assertEqual(findCurrentPresident(), P[1])
        self.assertEqual(findCurrentPresident(True), P[0])
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

    def test_policyPresidentDraw(self):
        """policyPresidentDraw() is a client-facing view. It first does an
        identity check to assure only the current president (previousPresident
        technically) has access to the three policy cards drawn from the top
        of the deck. It then returns a JsonResponse object pairing the cards
        with an index."""
        fivePlayerSetup()
        setUpMatch()
        setUpPolicyDeck()
        pres = Player.objects.get(name='test0')
        pres.previousPresident = True
        pres.save()
        information = policyPresidentDraw(None, pres.id).content
        information = information.decode('utf8')
        # print(information, type(information))
        self.assertEqual(len(PolicyDeck.objects.all()), 14)
        notPres = Player.objects.get(name='test1')
        notPres.president = True
        with self.assertRaises(AssertionError):
            policyPresidentDraw(None, notPres.id)
        information = policyPresidentDraw(None, pres.id).content
        self.assertEqual(len(PolicyDeck.objects.all()), 11)
        information = policyPresidentDraw(None, pres.id).content
        self.assertEqual(len(PolicyDeck.objects.all()), 8)
        information = policyPresidentDraw(None, pres.id).content
        self.assertEqual(len(PolicyDeck.objects.all()), 5)
        information = policyPresidentDraw(None, pres.id).content
        self.assertEqual(len(PolicyDeck.objects.all()), 2)
        for i in range(15):
            x = DiscardPile(card="testLiberal")
            x.save()
        information = policyPresidentDraw(None, pres.id).content
        self.assertEqual(len(PolicyDeck.objects.all()), 14)
        clearAll()


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