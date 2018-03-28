from django.db import models

# Create your models here.
class Player(models.Model):
    """For database PLAYERS"""
    name = models.CharField(max_length=30)
    isAlive = models.BooleanField(default=True)
    president = models.BooleanField(default=False)
    chancellor = models.BooleanField(default=False)
    party = models.CharField(max_length=20, default="")
    role = models.CharField(max_length=20, default="")
    hasBeenInvestigated = models.BooleanField(default=False)
    previousPresident = models.BooleanField(default=False)



class GameState(models.Model):
    """Database representing the state of the board. Status int represents
    to client which activity to render at any given time."""
    libPolicyCount = models.IntegerField(default=0)
    fasPolicyCount = models.IntegerField(default=0)
    electionTracker = models.IntegerField(default=0)
    statusID = models.IntegerField(default=0)
    statusUpdate = models.CharField(max_length=200, default="")
    numberOfPlayers = models.IntegerField(default=0)
    chancellorNominated = models.CharField(max_length=30, default="")
    EX_AffiliationCheckOccurred1 = models.BooleanField(default=False)
    EX_AffiliationCheckOccurred2 = models.BooleanField(default=False)
    EX_SpecialElectionCalled = models.BooleanField(default=False)
    EX_PolicyPeekDone = models.BooleanField(default=False)
    EX_Exection1 = models.BooleanField(default=False)
    EX_Exection2 = models.BooleanField(default=False)
    lastPolicyPassed = models.CharField(max_length=20, default="")
    cardsForChancellor1 = models.CharField(max_length=20, default="")
    cardsForChancellor2 = models.CharField(max_length=20, default="")

class Voting(models.Model):
    """Database that handles election votes from players."""
    name = models.CharField(max_length=30, default="")
    vote = models.BooleanField(default=False) # None/null if not yet voted, True/False for Ja/Nien.

class PolicyDeck(models.Model):
    """Database to hold Policy Card Draw Deck. To be Populated with appropriate
    number of cards of all types (random.shuffle()) and drawn from highest pk first."""
    card = models.CharField(max_length=20, default="")

class DiscardPile(models.Model):
    """DiscardPile database. Once draw deck is depleted, this deck will be
    shuffled and reassigned to PolicyDeck"""
    card = models.CharField(max_length=20, default="")
        
class PresidentQueue(models.Model):
    """Database to hold the presidential order list. special is marked if
    a president is appointed by executive action."""
    playerID = models.IntegerField()
    special = models.BooleanField(default=False)

class Confirmation(models.Model):
    """Database for holding confirmation requests from view showEveryonesVotesConfirm/activity_results.xml."""
    playerID = models.IntegerField()
        