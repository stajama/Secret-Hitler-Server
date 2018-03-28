def votingMachine():
    """Worker function, collects all votes in Voting database. Returns
    results and voter/vote cast pairs in key:value format."""
    information = {}
    V = Voting.objects.all()
    for i in V:
        information[i.name] = i.vote
    if votingTally():
        information["result"] = "The vote passed."
    else:
        information["result"] = "The vote failed. Citizen frustration will increase."
    return information

def votingTally():
    """Worker function, counts all votes cast in election, determines pass/fail
    based on current number of living players vs. Ja votes cast. All votes 
    require a majority to pass."""
    V = Voting.objects.all()
    total = getLivingCount()
    count = 0
    for i in V:
        if i.vote:
            count += 1
    return count > total // 2

def getLivingCount():
    """Returns the count of all players with True .isAlive value in Players database."""
    P = Player.objects.all()
    count = 0
    for i in P:
        if i.isAlive:
            count += 1
    return count

def checkCurrentVotes():
    """Returns a list of all players who currently have a vote cast in Voting database."""
    votedList = []
    V = Voting.objects.all()
    for i in V:
        votedList.append(i.name)
    return votedList

def findCurrentPresident():
    """Worker function, returns the current presidents cursor entry from Players
    database. Throws an error if more than one player is president."""

    # TODO (2) Probably best to move the error check here to a proper unit test.
    P = Player.objects.all()
    freakOut = False
    answer = None
    for i in P:
        if freakOut and i.president:
            raise AssertionError("Multiple Current Presidents in database")
        elif i.president:
            answer = i
            freakOut = True
    if answer is None:
        raise ValueError("No president selected. Issue with findCurrentPresident().")
    return answer

def findCurrentChancellor():
    """Worker function, returns the current chancellors cursor entry from Players
    database. Throws an error if more than one player is chancellor."""

    # TODO (3) See TODO 2.
    P = Player.objects.all()
    freakOut = False
    answer = None
    for i in P:
        if freakOut and i.chancellor:
            raise AssertionError("Multiple Current Chancellors in database")
        elif i.chancellor:
            answer = i
            freakOut = True
    return answer

def getEligiblePlayerList(election=False, affiliation=False):
    """Worker function. Returns as key/value pairs all players eligible for
    various choice scenarios in game. election turns on checks that assure
    term-limited players are not available to select for chancellor nominations.
    affiliation turns on checks to assure that players who have already had their
    loyalty cards inspected cannot be selected again."""

    # Snap elections, affiliation checks and Assassinations have the same rules: 
    # as long as you are alive, you can be president or shot. Affiliation should 
    # never arise after players can be killed.

    information = {}
    P = Player.objects.all()
    for i in P:
        if election:
            if not i.president and i.isAlive and not i.chancellor and not i.previousPresident:
                information[i.id] = i.name
        elif affiliation:
            if i.isAlive and not i.president and not i.hasBeenInvestigated:
                information[i.id] = i.name
        else:
            if i.isAlive and not i.president:
                information[i.id] = i.name
    return information

def findPlayerID(name=None, role=None):
    """DESIRED FUNCTIONALITY: This function should act as a one-stop-shop 
    to quickly pull a players Player database cursor for editing/information
    retrieval. Ideally, function should accept pk ID number, name, or desired
    role and return the desired format for a query (i.e. a single entry for ID
    of name, id number for the player with the target name, an array of 
    people with the target role, etc.).

    CURRENT Functionality: Worker function that returns the id of the first player
    found in Player database that matches search criteria. name limits search to 
    players with target name. role limits search to players with target role."""
    P = Player.objects.all()
    if name != None:
        for i in P:
            if i.name == name:
                return i.id
    if role != None:
        for i in P:
            if i.role == role:
                return i.id

def setUpPolicyDeck():
    """Initialization function. Adds correct number of cards of each type to the
    PolicyDeck database in shuffled order."""
    deck = []
    for _ in range(6):
        deck.append("Liberal")
    for _ in range(11):
        deck.append("Fascist")
    random.shuffle(deck)
    for card in deck:
        x = PolicyDeck(card=card)
        x.save()
    return



def setUpMatch():
    """Initialization function. Adds the correct number of roles cards of each
    type to an array and assigns them randomly to players."""
    rolesList = {5: ["Liberal", "Liberal", "Liberal", "Fascist", "Hitler"],  
                 6: ["Liberal", "Liberal", "Liberal", "Liberal", "Fascist", "Hitler"],
                 7: ["Liberal", "Liberal", "Liberal", "Liberal", "Fascist", "Fascist", "Hitler"],
                 8: ["Liberal", "Liberal", "Liberal", "Liberal", "Liberal", "Fascist", "Fascist", "Hitler"],
                 9: ["Liberal", "Liberal", "Liberal", "Liberal", "Liberal", "Fascist", "Fascist","Fascist", "Hitler"],
                 10: ["Liberal", "Liberal", "Liberal", "Liberal", "Liberal", "Liberal", "Fascist", "Fascist","Fascist", "Hitler"]}
    G = GameState.objects.all()[0]
    roles = copy.copy(rolesList[G.numberOfPlayers])
    random.shuffle(roles)
    P = Player.objects.all()
    for player in P:
        player.role = roles[-1]

        roles.pop()
        if player.role == "Hitler":
            player.party = "Fascist"
        else:
            player.party = player.role
        player.save()
    return

def resetDeck():
    """Worker function, collects all cards placed in DiscardPile database,
    combines with remaining PolicyDeck database, shuffles, and rebuilds
    PolicyDeck with all remaining policy cards. Clears DiscardPile upon 
    completion."""
    allCards = []
    for i in DiscardPile.objects.all():
        allCards.append(i.card)
    for i in PolicyDeck.objects.all():
        allCards.append(i.card)
    x = DiscardPile.objects.all()
    x.delete()
    x.save()
    x = PolicyDeck.objects.all()
    x.delete()
    x.save()
    allCards = random.shuffle(allCards)
    for i in allCards:
        y = PolicyDeck(card=i)
        y.save()
    if not len(allCards) == len(PolicyDeck.objects.all()):
        raise AssertionError("lost or gained cards during shuffling")
    if not len(DiscardPile.objects.all()) == 0:
        raise AssertionError("DiscardPile not cleared")
    return

def playPolicyCard(card): # as String
    """Worker function. Accepts the string of the policy card to be played,
    adds it to the appropriate GameState._policyCount entry, updates the 
    statusUpdate with the policy enacted."""
    G = GameState.objects.all()[0]
    if card == "Fascist":
        G.fasPolicyCount += 1
        G.statusUpdate = "A Fascist policy was enacted!"
        G.save()
    else:
        G.libPolicyCount += 1
        G.statusUpdate = "A Liberal policy was enacted!"
        G.save()
    return

def drawCard():
    """Worker function. Removes one card from the PolicyDeck database. Useful
    for Presidential policy drawing (run 3 times) or election tracker auto-card
    play."""
    indexOf = len(PolicyDeck.objects.all())
    newCard = PolicyDeck.objects.get(pk=indexOf)
    x = PolicyDeck.objects.get(pk=indexOf).delete()
    x.delete()
    return newCard.card

def electionTrackerFull():
    """Worker function. Draws the first PolicyDeck card and plays it immediately."""
    x = drawCard()
    playPolicyCard(x)
    return x

def isGameOver():
    """Worker function, checks all win states in GameState: have enough Fascist policies
    been enacted, have enough Liberal policies been enacted, has Hitler become 
    Chancellor after 3 Fascist policies have been enacted, has Hitler been killed."""
    G = GameState.objects.all()[0]
    if G.fasPolicyCount >= 6:
        return True
    if G.fasPolicyCount >= 3 and findCurrentChancellor().role == "Hitler":
        return True
    if not Player.objects.get(pk=findPlayerID(role="Hitler")).isAlive:
        return True
    if G.libPolicyCount >= 5:
        return True
    return False

def executiveActions():
    """Worker function, checks all executive action conditions and alerts if something 
    extra must be done."""

    # TODO (4) Functionality here is not clear. Why does this have to exist?

    G = GameState.objects.all()[0]
    def executePlayer(gameObject):
        if gameObject.fasPolicyCount >= 4:
            if not gameObject.EX_Exection1:
                gameObject.EX_Exection1 = True
                gameObject.save()
                return True
            if not gameObject.EX_Exection2:
                gameObject.EX_Exection2 = True
                gameObject.save()
                return True
        return False

    def policyPeek(gameObject):
        if gameObject.numberOfPlayers == 5 or gameObject.numberOfPlayers == 6:
            if gameObject.fasPolicyCount >= 3 and not gameObject.EX_PolicyPeekDone:
                gameObject.EX_PolicyPeekDone = True
                gameObject.save()
                return True
        return False

    def selectNextPresident(gameObject):
        if gameObject.numberOfPlayers > 6 and gameObject.fasPolicyCount >= 3 and not gameObject.EX_SpecialElectionCalled:
            gameObject.EX_SpecialElectionCalled = True
            gameObject.save()
            return True
        return False

    def showPartyCard(gameObject):
        if gameObject.numberOfPlayers > 8 and gameObject.fasPolicyCount == 1 and not gameObject.EX_AffiliationCheckOccurred1:
            gameObject.EX_AffiliationCheckOccurred1 = True
            gameObject.save()
            return True
        elif gameObject.numberOfPlayers > 6 and gameObject.fasPolicyCount == 2 and not gameObject.EX_AffiliationCheckOccurred2:
            gameObject.EX_AffiliationCheckOccurred2 = True
            gameObject.save()
            return True
        return False

    if executePlayer(G):
        updateGStatusID(17)
        updateGStatusUpdate("The President must now select a player to execute.")
        return True
    elif policyPeek(G):
        updateGStatusID(16)
        updateGStatusUpdate("The President will now look at the top 3 policy cards in the Policy Deck.")
        return True
    elif selectNextPresident(G):
        updateGStatusID(15)
        updateGStatusUpdate("The President will now call for a Special Election. All players are eligible to be selected to be President.")
        return True
    elif showPartyCard(G):
        updateGStatusID(14)
        updateGStatusUpdate("The President will now look at the Party Affiliation of a player of their choosing (not your Role Card).")
        return True
    return None

def oneToTheBackOfTheHead(playerDBentry):
    """Function to change executed player isAlive status."""
    playerDBentry.isAlive = False
    playerDBentry.save()
    return

def showNextThreeCards():
    """Worker Function. Gathers information about top three cards in PolicyDeck
    for display. Returned as key/value pairs (index: value of card.)"""
    information = {}
    PD = PolicyDeck.objects.all()
    start = len(PD)
    if len(PD) < 3:
        resetDeck()
        PD = PolicyDeck.objects.all()
        start = len(PD)
    for i in range(3):
        information[i] = PD.get(pk=start)
        start -= 1
    return information

def cyclePresident():
    """Worker function. Updates Player database with current president, skips
    over any player who is not alive. Also filters out the special election
    presidential candidate by not adding special cases back into the queue."""
    nextInLine = PresidentQueue.objects.all()[0]
    lifeCheck = Player.objects.get(pk=nextInLine.playerID)
    if not lifeCheck.isAlive:
        nextInLine.delete()
        nextInLine.save()
        nextInLine = PresidentQueue.objects.all()[0]
    assign = Player.objects.get(pk=nextInLine.playerID)
    assign.president = True
    assign.save()
    if nextInLine.special:
        nextInLine.delete()
        nextInLine.save()
        return
    hold = nextInLine.playerID 
    nextInLine.delete()
    nextInLine.save()
    x = PresidentQueue(playerID=hold, special=False)
    x.save()
    return

def insertPresident(idNumber):
    """Worker Function. For special election handling. Adds selected candidate to
    the front of the PresidentQueue so the special election proceeds like normal
    elections."""
    hold = [(i.playerID, i.special) for i in PresidentQueue.objects.all()]
    PQ = PresidentQueue.objects.all()
    PQ.delete()
    PQ.save()
    x = PresidentQueue(playerID=idNumber, special=True)
    x.save()
    for i in hold:
        x = PresidentQueue(playerID=i[0], special=i[1])
        x.save()
    return

def setUpPresidentQueue():
    for player in Player.objects.all():
        x = PresidentQueue(playerID=player.id, special=False)
        x.save()
    return

def updateGStatusID(target):
    G = GameState.objects.all()[0]
    G.statusID = target
    G.save()
    return

def updateGStatusUpdate(message):
    G = GameState.objects.all()[0]
    G.statusUpdate = message
    G.save()
    return

################################### DEBUG TOOLS ################################

def debug_log_dump (playerDB=False, gameState=False, voting=False,
              policyDeck=False, discardPile=False, 
              presidentQueue=False):
    if playerDB:
        logging.debug("Player Database Current")
        P = Player.objects.all()
        logging.debug("size: " + str(len(P)))
        logging.debug("contents ----------------------- ")
        logging.debug("id = name = isAlive = president = chancellor = party = role = hasBeenInvestigated = previousPresident")
        for i in P:
            logging.debug('-----------------------------------')
            logging.debug(str(i.id) + " : " \
                          + i.name + " : " \
                          + str(i.isAlive) + " : " \
                          + str(i.president) + " : " \
                          + str(i.chancellor) + " : " \
                          + i.party + " : " \
                          + i.role + " : " \
                          + str(i.hasBeenInvestigated) + " : " \
                          + str(i.previousPresident))
    if gameState:
        logging.debug("GameState Database Current")
        G = GameState.objects.all()[0]
        logging.debug(str(G.libPolicyCount) + " : " \
                      + str(G.fasPolicyCount) + " : "\
                      + str(G.electionTracker) + " : "\
                      + str(G.statusID) + " : "\
                      + G.statusUpdate + " : "\
                      + str(G.numberOfPlayers) + " : "\
                      + G.chancellorNominated + " : "\
                      + str(G.EX_AffiliationCheckOccurred1) + " : "\
                      + str(G.EX_AffiliationCheckOccurred2) + " : "\
                      + str(G.EX_SpecialElectionCalled) + " : "\
                      + str(G.EX_PolicyPeekDone) + " : "\
                      + str(G.EX_Exection1) + " : "\
                      + str(G.EX_Exection2) + " : "\
                      + G.lastPolicyPassed + " : "\
                      + G.cardsForChancellor1 + " : "\
                      + G.cardsForChancellor2
                      )
    if voting:
        logging.debug("Voting Database Current")
        V = Voting.objects.all()
        logging.debug("size: " + str(len(V)))
        for i in V:
            logging.debug(i.name + " : " + str(i.vote))

    if policyDeck:
        logging.debug("PolicyDeck Database Current")
        PD = PolicyDeck.objects.all()
        logging.debug("size: " + str(len(PD)))
        for i in PD:
            logging.debug(str(i.id) + ": " + i.card)

    if discardPile:
        logging.debug("DiscardPile Database Current")
        DP = DiscardPile.objects.all()
        logging.debug("size: " + str(len(DP)))
        for i in DP:
            logging.debug(str(i.id) + ": " + i.card)

    if presidentQueue:
        logging.debug("PresidentQueue Database Current")
        PQ = PresidentQueue.objects.all()
        logging.debug("size: " + str(len(PQ)))
        for i in PQ:
            logging.debug(str(i.playerID) + " - " + str(i.special))
    return

def debug_no_one_is_president():
    P = Player.objects.all()
    for i in P:
        if i.president:
            return False
    return True

def debug_statusID_check(callingFunction):
    logging.info("start of {0}, GameState.statusID: ".format(callingFunction) 
        + str(GameState.objects.all()[0].statusID))
    return

def debug_identity_check(id, chancellor=False):
    if not chancellor:
        if not id == findCurrentPresident().id:
            raise AssertionError("non president got to nomination screen")
        return
    else:
        if not id == findCurrentChancellor().id:
            raise AssertionError("non chancellor got to nomination screen")
        return

def thisFunction():
    return