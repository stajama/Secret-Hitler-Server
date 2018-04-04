from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from .models import Player, GameState, Voting, PolicyDeck, DiscardPile, PresidentQueue, Confirmation

import time
import random
import copy
import logging
import bleach

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s \
    - %(levelname)s - %(message)s')

# Create your views here.

def get(request):
    return HttpResponse("Hello World!")

def setup(request, confirm=0, playerCount=0):
    """Initial setup call. Received from activity_main.xml or activity_end.xml,
    this checks if a game is already in progress (requires confirmation 
    [confirm=1]) to overwrite game in progress), clears all databases, and
    initializes the GameState object and sets the statusID to 2 (accepting 
    players). Returns HttpResponses 'confirm' 'override.'"""

    if not len(Player.objects.all()) == 0:
        if confirm:
            getResources(playerCount)
            return HttpResponse('confirm')
        else:
            return HttpResponse("override")
    else:
        getResources(playerCount)
        return HttpResponse('confirm')

######################################## Client Facing Views ##################################

def joinGame(request, pname=None):
    """Should be called from activity_joining:button_joining_accept_name. Accepts 
    url/playername and adds player to Player database. Returns the player's pk id
    for the app to use in future."""
    pname = bleach.clean(pname)
    pname = cleanSpaces(pname)
    if pname != None and GameState.objects.all()[0].statusID == 2:
        x = Player(name=pname, isAlive=True, president=False, chancellor=False, 
                   party="", role="", hasBeenInvestigated=False)
        x.save()
        '''3/19 refactor: instead of a silly looping view as before, the server will
        update status through the client views when the appropriate conditions are
        met. Here, once the game is full, the statusID is set to 3 (base/president
        nomination phase).'''
        if len(Player.objects.all()) == GameState.objects.all()[0].numberOfPlayers:
            finalizeResources() 
        return HttpResponse(x.id)
    return HttpResponse("Unable to join, game is full.")

def client_status(request, id):
    """General update view. Client will probably call this repeated for statusID
    update checks."""
    # TODO (1) GameState.statusUpdate should probably be added here.
    # information = worker.getStatus(id)
    return getStatus(id)

def headsUpToVote(request):
    """This view, attached to statusID 6, is paired to app:activity_voting.xml. 
    HttpResponse string can likely just be used for text for text_president_chancellor TextView"""
    G = GameState.objects.all()[0]
    return HttpResponse(G.statusUpdate)

def submitVote(request, id, voting):
    """Called by app:activity_voting.xml, button_voting_ja requests url/id/1,
    button_voting_nien requests url/id/0. This view stores the vote in the
    Voting database for later display."""
    P = Player.objects.get(pk=id)
    if P.name in checkCurrentVotes():
        return HttpResponse("error")
    if voting == "1" or voting == 1:
        voting = True
    else:
        voting = False
    P = Player.objects.get(pk=id)
    voter = P.name
    logging.debug(f"submitVote: {str(id)}, {P.name} vote received: {str(voting)}")
    V = Voting(name=voter, vote=voting)
    logging.debug(f"submitVote: proof data saved: " + str(V))    
    V.save()
    if len(Voting.objects.all()) == getLivingCount():
        votingFinished()
    return HttpResponse("confirm")

'''3/19 refactor: showEveryonesVotes() will be called on statusIDs 99 and 98
(vote pass and fail, respectively). This view will assure that every players
sees the votes that other players submitted with time to study and review this
information. Additional, the activity_results.xml view should come with a
confirm button. Once all players have confirmed, statusID will update to 9 or
3 (policyHandling or back to presidential nomination).'''
def showEveryonesVotes(request):
    """Returns a JSON response of the result of the vote and how everyone
    voted in the current election. Non-'information' results to populate 
    @+id/scroll_results_vote_list ScrollView."""
    return JsonResponse(votingMachine())

def showEveryonesVotesConfirm(request, id):
    # debug_log_dump(gameState=True, confirmation=True)
    if not checkConfirmationList(id):
        confirmView(id)
    G = GameState.objects.all()[0]
    if len(Confirmation.objects.all()) == G.numberOfPlayers:
        Voting.objects.all().delete()
        Confirmation.objects.all().delete()
        if isGameOver():
            return HttpResponse('confirm')
        # debug_log_dump(voting=True)
        if G.statusID == 99:
            updateGStatusID(9)
        elif G.statusID == 98:
            updateGStatusID(3)
            updateGStatusUpdate(f'The current President is {findCurrentPresident().name}. Waiting for the President to nominate a Chancellor.')
        else:
            raise AssertionError("Don't know how we got here. showEveryonesVotesConfirm(), statusID not 99 or 98: " + str(G.statusID))
    return HttpResponse('confirm')

'''3/19 refactor: everyone now views this view update statusID = 9. 
Only the president will receive the JsonResponse with policy cards to inspect.'''
def policyPresidentDraw(request, id):
    """For presidents eyes only. Draws 3 cards from PolicyDeck database,
    returns these cards in JSON response for review and selection."""
    G = GameState.objects.all()[0]
    if id == findCurrentPresident(True).id:
        if len(PolicyDeck.objects.all()) < 3:
            resetDeck()
        hand = {}
        for i in range(1, 4):
            hand[i] = drawCard()
        hand['information'] = 'Select a policy card to discard. The remaining cards will be passed to the Chancellor.'
        hand['wait'] = ''
        return JsonResponse(hand)
    else:
        information = {}
        information['wait'] = f"Waiting for President {findCurrentPresident(True).name} to select policies."
        return JsonResponse(information)

def policyPresidentSelect(request, id, passing1, passing2, discarded):
    """For presidents eyes only. app:activity_policy_selection.xml will return 
    url/not_selected_card/not_selected_card/selected_card. This view sends the
    selected card to the DiscardPile database, sends the not selected cards to the 
    GameState.cardsForChancellor1/cardsForChancellor2 slots. Updates statusID to allow
    chancellor access to policyChancellorDraw()."""
    debug_identity_check(id, post=True)
    logging.error(f"Catastrophe: policyPresidentSelect: passing1 = {passing1}, passing2 = {passing2}, discarded = {discarded}")
    DP = DiscardPile(card=discarded)
    logging.debug("policyPresidentSelect: Something wrong with DB? - " + DP.card + " " + str(type(DP.card)))
    DP.save()
    G = GameState.objects.all()[0]
    G.cardsForChancellor1 = passing1
    G.cardsForChancellor2 = passing2
    G.save()
    updateGStatusID(10)
    updateGStatusUpdate("Waiting for the Chancellor to select a policy.")
    return HttpResponse("confirm")

'''3/19 refactor: everyone now views this view update statusID = 10 (or statusID 12 [president denies veto]). 
Only the Chancellor will receive the JsonResponse with policy cards to inspect.'''
def policyChancellorDraw(request, id):
    """For Chancellor's eyes only. Sends the two cards from GameState.cardsForChancellor1
    holders for review and selection as a JSON response. If veto powers are available, also
    packages that information in JSON response."""
    if Player.objects.get(pk=id).chancellor:
        G = GameState.objects.all()[0]
        hand = {}
        hand[1] = G.cardsForChancellor1
        hand[2] = G.cardsForChancellor2
        hand['information'] = 'Select a policy card to enact.'
        hand['wait'] = ''
        if G.fasPolicyCount >= 5 and G.statusID != 12:
            hand["veto"] = True
            hand["vetoText"] = "You may veto these policies if the President consents."
        elif G.fasPolicyCount >= 5 and G.statusID == 12:
            hand["veto"] = False
            hand["vetoText"] = "The President has declined your request to veto. You MUST select a policy to enact."
        else:
            hand["veto"] = False
            hand["vetoText"] = ""
        return JsonResponse(hand)
    else:
        G = GameState.objects.all()[0]
        information = {}
        if G.statusID == 12:
            information['wait'] = "The President has declined the Chancellor's request to veto the current agenda. The Chancellor MUST select a policy to enact."
        else:
            information['wait'] = f"Waiting for Chancellor {findCurrentChancellor().name} to select a policy."
        return JsonResponse(information)

def policyChancellorSelects(request, id, passCard, discard):
    """If the veto button is not selected, this view if called. Discarded the non-selected
    card to the DiscardPile, plays the selected card. Returns statusID to 3 to restart gameloop."""
    debug_identity_check(id, chancellor=True)
    logging.error(f"Catastrophe: policyChancellorSelect: passCard = {passCard}, discard = {discard}")

    DP = DiscardPile(card=discard)
    logging.debug("policyChancellorSelect: Something wrong with DB? - " + DP.card + " --- " + str(type(DP.card)))
    DP.save()
    G = GameState.objects.all()[0]
    playPolicyCard(passCard)
    updateGStatusID(97) # statusID 97 will now be used to push all clients to policyResultView().
    return HttpResponse("confirm")

def policyChancellorVeto(request, id):
    """View is call if Chancellor selects to veto current cards. Status updates G.statusID
    and G.statusUpdate."""
    debug_identity_check(id, chancellor=True)
    updateGStatusID(11)
    updateGStatusUpdate("The Chancellor has requested to veto the current agenda.")
    return HttpResponse("Awaiting president response")

def policyVetoPresident(request, id):
    """Should load only for president on statusID 11. Chancellor has requested a 
    veto and requires presidential approval."""
    if id == findCurrentPresident(True).id:
        return HttpResponse("Chancellor {0} has requested to veto the current set of policies. Do you accept?"
           .format(findCurrentChancellor().name))
    else:
        return HttpResponse("Awaiting president response")

def policyVetoChoice(request, id, choice):  # choice will probably have to be a binary.
    """View called by president veto yes/no button. (url/choice [0, 1]). Updates 
    statusID to 12 - denied, and 13 - approved. Game loop restarted in server 
    view policyHandling()."""
    debug_identity_check(id, post=True)
    G = GameState.objects.all()[0]
    if choice:
        updateGStatusID(13)
        updateGStatusUpdate(f"President {findCurrentPresident(True).name} and Chancellor {findCurrentChancellor().name} have decided to veto the current agenda. The election tracker will increase by 1.")
        updateElectionTracker()
        return HttpResponse("veto successful")
    else:
        updateGStatusID(12)
        updateGStatusUpdate("The President has declined the Chancellor's request to veto the current agenda. The Chancellor MUST select a policy to enact.")
        return HttpResponse("veto denied")

# 3/27 post refactor. policyResultsView is now to be called after 13 as well (president oks veto).
def policyResultsView(request): 
    return HttpResponse('confirm')

def policyResultsConfirm(request, id):
    logging.debug('confirmation received from ' + str(id))
    if not checkConfirmationList(id):
        confirmView(id)
    G = GameState.objects.all()[0]
    # debug_log_dump(confirmation=True)
    if len(Confirmation.objects.all()) == G.numberOfPlayers:
        Confirmation.objects.all().delete()
        if isGameOver():
            return HttpResponse('Game Over')
        logging.debug("all confirmations received.")
        if executiveActions():
            print('tick')
            return HttpResponse('moving to Executive Powers')
        updateGStatusID(3)
        updateGStatusUpdate(f'The current President is {findCurrentPresident().name}. Waiting for the President to nominate a Chancellor.')
    return HttpResponse('confirm')

'''3/19 refactor: everyone now views this view update statusID = 17. 
Only the president will receive the JsonResponse with eligible execution targets.'''
def executiveExecution(request, id):
    """View called if statusID 17 called. Sends JSON data: list of all living players,
    instructions for execution."""
    if id == findCurrentPresident(True).id:
        information = getEligiblePlayerList()
        information["information"] = "You must now execute a player."
        information['wait'] = ''
        return JsonResponse(information)
    else:
        information = {}
        information["information"] = GameState.objects.all()[0].statusUpdate
        information['wait'] = '1'
        return JsonResponse(information)

def executiveExecutionOrder(request, id, selected):
    """View called by presidential selection from activity_player_selection.xml. 
    selected is pk ID of player to be executed. 'Sucks to be you...'"""
    debug_identity_check(id, post=True)
    G = GameState.objects.all()[0]
    updateGStatusID(3)
    unluckyOne = Player.objects.get(pk=selected)
    if not unluckyOne.isAlive:
        raise AssertionError('dead men can not be killed. Again. Generally speaking...')
    if unluckyOne.president:
        unluckyOne.president = False
        cyclePresident()
        logging.error('CHECK PRESIDENT QUEUE FOR ZOMBIES')
        # debug_log_dump(playerDB=True, presidentQueue=True)
    logging.debug("in executiveExecutionOrder(), info for unluckyone: " + unluckyOne.name + ' ' + str(unluckyOne.id))
    updateGStatusUpdate(f"The President has selected {unluckyOne.name} for immediate execution.")
    oneToTheBackOfTheHead(unluckyOne)
    isGameOver()
    return HttpResponse('confirm')

'''3/19 refactor: everyone now views this view update statusID = 14. 
Only the president will receive the JsonResponse with policy cards to inspect.'''
def executiveAffiliationLook(request, id):
    """View called by statusID 14. Returns to president for activity_player_selection.xml
    JSON data: instructions for party peek, list of all eligible players to 
    inspect."""
    if Player.objects.get(pk=id).president:
        information = getEligiblePlayerList(affiliation=True)
        information["information"] = "You may now check the party affiliation card of any other player."
        information['wait'] = ''
        return JsonResponse(information)
    else:
        information = {}
        information["information"] = GameState.objects.all()[0].statusUpdate
        information['wait'] = '1'
        return JsonResponse(information)

def executiveAffiliationLookOrder(request, id, selected):
    """View called by president activity_player_selection.xml selection.
    selected is pk ID of selected player. Their party information is returned
    to president via HttpResponse."""
    debug_identity_check(id, post=True)
    G = GameState.objects.all()[0]
    updateGStatusID(3)
    updateGStatusUpdate("The President has selected to investigate the party affiliations of {0}.".format(
                        Player.objects.get(pk=selected).name))
    return HttpResponse(Player.objects.get(pk=selected).name + " is a filthy " \
                        + Player.objects.get(pk=selected).party + "!")

'''3/19 refactor: everyone now views this view update statusID = 16. 
Only the president will receive the JsonResponse with policy cards to inspect.'''
def executivePolicyPeek(request, id):
    """View called by statusID 16 to president only. Shows the top three
    cards in the policy deck to the president. Does not alter the deck."""
    if id == findCurrentPresident(True).id:
        information = showNextThreeCards()
        logging.info('in executivePolicyPeek() for president: information dict: ' + str(information))
        information["information"] = "You may now peek at the next three policy cards in the policy deck."
        information['wait'] = ''
        logging.info('executivePolicyPeek(): final: ' + str(information))
        return JsonResponse(information)
    else:
        information = {}
        information["information"] = GameState.objects.all()[0].statusUpdate
        information['wait'] = '1'
        return JsonResponse(information)

'''refactor follow up 3/26, we require a president confirmation to move statusID back to 3 after policy peek.'''
def executivePolicyPeekConfirmation(request, id):
    debug_identity_check(id, post=True)
    updateGStatusID(3)
    updateGStatusUpdate(f'The current President is {findCurrentPresident().name}. Waiting for the President to nominate a Chancellor.')
    return HttpResponse('confirm')

'''3/19 refactor: everyone now views this view update statusID = 15. 
Only the president will receive the JsonResponse with policy cards to inspect.'''
def executiveSpecialElection(request, id):
    """View called by statusID 15. JSON data sent to president for 
    activity_player_selection.xml: instruction for special election, list of
    all eligible players."""
    if Player.objects.get(pk=id).president:
        information = getEligiblePlayerList()
        information["information"] = "You may now call a special election. Select a candidate to run for President."
        information['wait'] = ''
        return JsonResponse(information)
    else:
        information = {}
        information["information"] = GameState.objects.all()[0].statusUpdate
        information['wait'] = '1'
        return JsonResponse(information)

def executiveSpecialElectionOrder(request, id, selected):
    """View called by president activity_player_selection.xml selection.
    selected is pk ID of selected player. The player is inserted into the 
    front of the line of PresidentQueue database with special=True. 
    Updates statusID to 2."""
    debug_identity_check(id, post=True)
    G = GameState.objects.all()[0]
    insertPresident(selected)
    updateGStatusID(3)
    updateGStatusUpdate("The President has selected {0} to server as the next President.".format(
                        Player.objects.get(pk=selected)))
    return HttpResponse('confirm')

def nominateChancellor(request, id):
    """View called by activity_base.xml (statusID = 3). Only the
    president will receive a JsonResponse list of eligible chancellor
    nominees; other players will have this list hidden on their screen
    and await the time-to-vote status update (statusID = 6)"""
    # debug_identity_check(id)
    if isGameOver():
        return 'Game Over'
    information = {}
    if id == findCurrentPresident().id:
        information = getEligiblePlayerList(election=True)
        information["information"] = "You may now nominate a candidate for Chancellor."
        information['wait'] = ''
    else:
        information['wait'] = '1'
    return JsonResponse(information)

def nominateChancellorOrder(request, id, selected):
    # debug_log_dump(gameState=True)
    debug_identity_check(id)
    G = GameState.objects.all()[0]
    G.chancellorNominated = Player.objects.get(pk=selected).name
    G.save()
    updateGStatusID(6)
    updateGStatusUpdate(f"{findCurrentPresident().name} nominated {Player.objects.get(pk=selected).name} for Chancellor.")
    # debug_log_dump(gameState=True)
    return HttpResponse("confirm")

def gameIsOver(request):
    """Corresponses to statusID 100. One of the victory conditions have been met and the game is over."""
    return JsonResponse(getAllInfo())

######################################## Worker functions #####################################

"""3/19 refactor: the functionality of getStatus has been mixed with the
original intent of roleSpecificRequest(), now constantly updating the client
with statusID,  statusUpdate message, and secret information."""
def getStatus(id):
    """Function that pulls requesting player's name, party, role, the
    GameState.statusID, and GameState.statusUdpdate. Also includes secret
    information for Fascist players. Packaged in JsonResponse object."""
    logging.debug(str(id))
    logging.error('Start of getStatus() possible error here.')
    debug_log_dump(playerDB=True, gameState=True)
    G = GameState.objects.all()[0]
    if G.statusID == 2:
        return JsonResponse({'statusID': 2})
    P = Player.objects.get(pk=id)
    information = {}
    information["livingPlayerCount"] = getLivingCount()
    information["id"] = P.id
    information["name"] = P.name
    information["party"] = P.party
    information["role"] = P.role
    information["alive"] = P.isAlive
    information["statusID"] = G.statusID
    information["statusUpdate"] = G.statusUpdate
    information["fasPolicies"] = G.fasPolicyCount
    information["libPolicies"] = G.libPolicyCount
    information["electionTracker"] = G.electionTracker
    if P.role == "Liberal":
        return JsonResponse(information)
    elif P.role == "Hitler":
        if G.numberOfPlayers == 5 or G.numberOfPlayers == 6:
            information.setdefault("Other Fascists", "")
            for i in Player.objects.all():
                if i.party == "Fascist" and i.role != "Hitler":
                    information["Other Fascists"] += i.name
        return JsonResponse(information)
    else:
        information["Hitler"] = Player.objects.get(pk=findPlayerID(role="Hitler")).name
        information["Other Fascists"] = ""
        for i in Player.objects.all():
            if i.party == "Fascist" and i.role == "Fascist":
                information["Other Fascists"] += i.name + ", "
        information["Other Fascists"] = information["Other Fascists"][ : -2] 
        # This is intended to cut off the trailing ', ' inevitable with this Fascist collection method.
        return JsonResponse(information)

def votingMachine():
    """Worker function, collects all votes in Voting database. Returns
    results and voter/vote cast pairs in key:value format."""
    information = {}
    G = GameState.objects.all()[0]
    V = Voting.objects.all()
    information['number of votes'] = len(V)
    for i in V:
        information[i.name] = i.vote
    if G.statusID == 99:
        information["result"] = "The vote passed."
    elif G.statusID == 98:
        information["result"] = "The vote failed. Citizen frustration will increase."
    else:
        raise AssertionError('dont know how we got here, votingMachine(), no vote result status ID')
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

def findCurrentPresident(post=False):
    """Worker function, returns the current presidents cursor entry from Players
    database. Throws an error if more than one player is president."""

    # TODO (2) Probably best to move the error check here to a proper unit test.
    # logging.debug("----------- START OF findCurrentPresident() --------------\npost on: " + str(post))
    # debug_log_dump(playerDB=True)
    P = Player.objects.all()
    freakOut = False
    answer = None
    for i in P:
        logging.debug('looking at ' + i.name + ", " + str(i.id) + "; has a match been found: " + str(freakOut))
        if post:
            if i.previousPresident and freakOut:
                raise AssertionError("Multiple Current Presidents in database")
            elif i.previousPresident:
                logging.debug(i.name + ' is previous president')
                answer = i
                freakOut = True
        else:
            if freakOut and i.president:
                raise AssertionError("Multiple Current Presidents in database")
            elif i.president:
                logging.debug(i.name + ' is current president')
                answer = i
                freakOut = True
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
            if getLivingCount() > 5:
                if not i.president and i.isAlive and not i.chancellor and not i.previousPresident:
                    information[i.id] = i.name
            else:
                if not i.president and i.isAlive and not i.chancellor:
                    information[i.id] = i.name
        elif affiliation:
            if i.isAlive and not i.previousPresident and not i.hasBeenInvestigated:
                information[i.id] = i.name
        else:
            if i.isAlive and not i.previousPresident:
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
    x = PolicyDeck.objects.all()
    x.delete()
    random.shuffle(allCards)
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
    newCard = PolicyDeck.objects.all()[indexOf - 1]
    x = PolicyDeck.objects.all()[indexOf - 1].delete()
    return newCard.card

def electionTrackerFull():
    """Worker function. Draws the first PolicyDeck card and plays it immediately."""
    x = drawCard()
    playPolicyCard(x)
    G = GameState.objects.all()[0]
    G.electionTracker = 0
    G.save()
    return x

def isGameOver():
    """Worker function, checks all win states in GameState: have enough Fascist policies
    been enacted, have enough Liberal policies been enacted, has Hitler become 
    Chancellor after 3 Fascist policies have been enacted, has Hitler been killed."""
    G = GameState.objects.all()[0]
    if G.fasPolicyCount >= 6:
        logging.error('Game over for fascist policy win. state should be 100')
        updateGStatusUpdate("The Fascists have achieved a policy victory.")
        updateGStatusID(100) # New status for Game Over.
        return True
    if G.fasPolicyCount >= 3 and findCurrentChancellor().role == "Hitler":
        logging.error('Game over for fascist election win. state should be 100')
        updateGStatusUpdate("The Fascists have achieved victory by getting Hitler elected Chancellor.")
        updateGStatusID(100) # New status for Game Over.
        return True
    if not Player.objects.get(pk=findPlayerID(role="Hitler")).isAlive:
        logging.error('Game over for liberal "fuck Hitler" win. state should be 100')
        updateGStatusUpdate("The Liberals have achieved victory by assassinating Hitler.")
        updateGStatusID(100) # New status for Game Over.
        return True
    if G.libPolicyCount >= 5:
        logging.error('Game over for liberal policy win. state should be 100')
        updateGStatusUpdate("The Liberals have achieved a policy victory.")
        updateGStatusID(100) # New status for Game Over.
        return True
    logging.info('no game-end status change')
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
    return False

def oneToTheBackOfTheHead(playerDBentry):
    """Function to change executed player isAlive status."""
    playerDBentry.isAlive = False
    playerDBentry.save()
    '''So that voting/etc does not break with a player is executed, the number
    of total players in decreased. This is a easier refactor than introducing
    a new "living player count" table entry, but may not work in the long run.'''

    # OBSOLETE - getLivingCount() should be used for such instances.
    return

def showNextThreeCards():
    """Worker Function. Gathers information about top three cards in PolicyDeck
    for display. Returned as key/value pairs (index: value of card.)"""
    information = {}
    PD = PolicyDeck.objects.all().reverse()[ : 3]
    if len(PD) < 3:
        resetDeck()
        PD = PolicyDeck.objects.all().reverse()[ : 3]
    for i in range(3):
        logging.info(str(i) + " : " + PD[i].card)
        information[i + 1] = PD[i].card
    return information

def cyclePresident():
    """Worker function. Updates Player database with current president, skips
    over any player who is not alive. Also filters out the special election
    presidential candidate by not adding special cases back into the queue."""
    logging.error('start of cyclePresident()')
    # debug_log_dump(playerDB=True)
    hold = [(i.playerID, i.special) for i in PresidentQueue.objects.all()]
    PresidentQueue.objects.all().delete()
    x = Player.objects.get(pk=hold[0][0])
    special = hold[0][1]
    while not x.isAlive:
        logging.error("cyclePresident(): someone is dead: " + f'{x.name} is not alive. Cycling to next presidential candidate.')
        hold.pop(0)
        x = Player.objects.get(pk=hold[0][0])
        special = hold[0][1]
        logging.error("cyclePresident(): someone is dead2: " + f'{x.name} is the next candidate')
    x.president = True
    x.save()
    if not special:
        hold = hold[1 : ] + [(x.id, False)]
    else:
        hold = hold[1 : ]
    for i in hold:
        y = PresidentQueue(playerID=i[0], special=i[1])
        y.save()
    return

def insertPresident(idNumber):
    """Worker Function. For special election handling. Adds selected candidate to
    the front of the PresidentQueue so the special election proceeds like normal
    elections."""
    hold = [(i.playerID, i.special) for i in PresidentQueue.objects.all()]
    PQ = PresidentQueue.objects.all().delete()
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

def getResources(num):
    Player.objects.all().delete()
    GameState.objects.all().delete()
    Voting.objects.all().delete()
    PresidentQueue.objects.all().delete()
    PolicyDeck.objects.all().delete()
    DiscardPile.objects.all().delete()
    Confirmation.objects.all().delete()
    G = GameState(libPolicyCount=0, fasPolicyCount=0, electionTracker=0, 
                  statusID=1, numberOfPlayers=num, chancellorNominated="",
                  EX_AffiliationCheckOccurred1=False, EX_AffiliationCheckOccurred2=False,
                  EX_SpecialElectionCalled=False, EX_PolicyPeekDone=False,
                  EX_Exection1=False, EX_Exection2=False, statusUpdate="", lastPolicyPassed="")
    G.save()
    updateGStatusID(2)
    return

def finalizeResources():
    setUpMatch()
    logging.info("start(): setUpMatch() run.")
    setUpPolicyDeck()
    logging.info("start(): setUpPolicyDeck() run.")
    setUpPresidentQueue()
    logging.info("start(): setUpPresidentQueue() run.")
    cyclePresident()
    updateGStatusUpdate(f"The current President is {findCurrentPresident().name}. Waiting for the President to nominate a Chancellor.")
    updateGStatusID(3)
    return

def confirmView(id):
    x = Confirmation(playerID=id)
    x.save()
    return True

def checkConfirmationList(id):
    hasConfirmed = False
    currentList = Confirmation.objects.all()
    for i in currentList:
        if i.playerID == id:
            hasConfirmed = True
    return hasConfirmed

def updateElectionTracker():
    G = GameState.objects.all()[0]
    G.electionTracker += 1
    G.save()
    return

def resetElectionTracker():
    G = GameState.objects.all()[0]
    G.electionTracker = 0
    G.save()
    return

def votingFinished():
    G = GameState.objects.all()[0]
    V = Voting.objects.all()
    P = Player.objects.all()
    logging.info("---------------------------")
    logging.info("Voting completed.")
    logging.info("---------------------------")
    if votingTally():
        # debug_log_dump(playerDB=True, voting=True)
        resetElectionTracker()
        currentChanceller = findCurrentChancellor()
        if currentChanceller != None:
            currentChanceller.chancellor = False
            currentChanceller.save()
        currentPreviousPresident = findCurrentPresident(True)
        if currentPreviousPresident != None:
            currentPreviousPresident.previousPresident = False
            currentPreviousPresident.save()
        newChancerllor = Player.objects.get(pk=findPlayerID(G.chancellorNominated))
        newChancerllor.chancellor = True
        lastPresident = findCurrentPresident()
        lastPresident.previousPresident = True
        lastPresident.president = False
        G = GameState.objects.all()[0]
        G.chancellorNominated = ""
        G.save(), lastPresident.save(), newChancerllor.save()
        updateGStatusID(99) # Changing to statusID 99 (vote passed)
        updateGStatusUpdate(f"Vote passed. President {findCurrentPresident(True).name} and Chancellor {findCurrentChancellor().name} will now enact a policy decision.")
        cyclePresident() 
        '''Cycling the presidency now because findCurrentPresident(post=True) 
        should prevent bugs where the upcoming president gets current 
        policy-enacting president's powers/views/etc.'''
        # debug_log_dump(playerDB=True, voting=True, gameState=True)        
        # return policyHandling(request)
        logging.info('vote passed')
        return
    else:
        logging.info('vote failed, performing clean up')
        updateGStatusUpdate("The election has failed. The election tracker will increase by 1.")
        logging.info(f'votingFinished() clean up 1: check : \n{"The election has failed. The election tracker will increase by 1."}\n vs.\n{GameState.objects.all()[0].statusUpdate}\n')
        updateElectionTracker()
        logging.info(f'votingFinished() clean up 2.0: check : \n{"The election has failed. The election tracker will increase by 1."}\n vs.\n{GameState.objects.all()[0].statusUpdate}\n')
        currentPresident = findCurrentPresident()
        currentPresident.president = False
        currentPresident.save()
        # logging.info(f'votingFinished() clean up 2: check current electionTracker count: {GameState.objects.all()[0].electionTracker}')
        G = GameState.objects.all()[0]
        G.chancellorNominated = ""
        G.save()
        logging.info(f'votingFinished() clean up 2.1: check : \n{"The election has failed. The election tracker will increase by 1."}\n vs.\n{GameState.objects.all()[0].statusUpdate}\n')
        # logging.info(f'votingFinished() clean up 3: check current "chancellorNominated" is empty: {GameState.objects.all()[0].chancellorNominated}')
        if G.electionTracker >= 3:
            # logging.info(f'votingFinished() clean up 3.5: electionTracker full?')
            x = electionTrackerFull()
            updateGStatusUpdate(G.statusUpdate + " The people have enacted a {0} policy!".format(x))
            logging.info(f'votingFinished() clean up 3: check : \n{"The election has failed. The election tracker will increase by 1."}\n vs.\n{GameState.objects.all()[0].statusUpdate}\n')
            # logging.info(f'votingFinished() clean up 3.5.1: check electionTracker = 0: {GameState.objects.all()[0].electionTracker}\n check that status is :" The people have enacted a "blank" policy!: {GameState.objects.all()[0].statusUpdate}')
        updateGStatusID(98) # Changing to statusID 98 (vote failed)
        # logging.info(f'votingFinished() clean up 4: check that statusID is actually 98: {GameState.objects.all()[0].statusID}')
        logging.info(f'votingFinished() clean up 4: check : \n{"The election has failed. The election tracker will increase by 1."}\n vs.\n{GameState.objects.all()[0].statusUpdate}\n')
        cyclePresident()
        logging.info(f'votingFinished() clean up 5: check : \n{"The election has failed. The election tracker will increase by 1."}\n vs.\n{GameState.objects.all()[0].statusUpdate}\n')
        '''Cycling the presidency now because findCurrentPresident(post=True) 
        should prevent bugs where the upcoming president gets current 
        policy-enacting president's powers/views/etc.'''
        # return base(request)
        logging.info(f'votingFinished() clean up 6: check : \n{"The election has failed. The election tracker will increase by 1."}\n vs.\n{GameState.objects.all()[0].statusUpdate}\n')
        logging.info(f'votingFinished() clean up: COMPLETE')
        return

def getAllInfo():
    information = {}
    for i in Player.objects.all():
        hold = 'Alive' if i.isAlive else 'Dead'
        information[i.name] = f'{i.name} : {i.role} : {hold}'
    G = GameState.objects.all()[0]
    information['fasPolicyCount'] = G.fasPolicyCount 
    information['libPolicyCount'] = G.libPolicyCount
    information['whatHappened'] = G.statusUpdate
    return information

def noZombiePresident():
    PQ = PresidentQueue.objects.all()[0]
    checking = Player.objects.get(pk=PQ.playerID)
    if not checking.isAlive:
        checking.president = False
        checking.save()
        cyclePresident()
    return

def cleanSpaces(input):
    while input.find("_") != -1:
        input = input[ : input.find("_")] + " " + input[input.find("_") + 1 : ]
    return input

################################### DEBUG TOOLS ################################

def debug_log_dump(playerDB=False, gameState=False, voting=False,
    policyDeck=False, discardPile=False, 
    presidentQueue=False, confirmation=False):
    """Debugging tool. Dumps all database information to the server log."""
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
    
    if confirmation:
        logging.debug("Current Confirmation Listing")
        conf = Confirmation.objects.all()
        logging.debug("current size: " + str(len(conf)))
        for i in conf:
            logging.debug(str(i.playerID))
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

def debug_identity_check(id, chancellor=False, post=False):
    if not chancellor:
        if not id == findCurrentPresident(post).id:
            raise AssertionError("non president got to nomination screen")
        return
    else:
        if not id == findCurrentChancellor().id:
            raise AssertionError("non chancellor got to nomination screen")
        return

def mockData1():
    '''5 player standard test'''
    players = 'abcde'
    roles = ['Liberal', 'Liberal', 'Liberal', 'Fascist', 'Hitler']
    for i in range(len(players)):
        x = Player.objects.get(name=players[i])
        x.role = roles[i]
        if roles[i] == 'Hitler':
            x.party = 'Fascist'
        else:
            x.party = roles[i]
        x.save()
    return HttpResponse('')

'''Death and inactivity will be handled client-side. If your status report
lists you as dead, all of your submission-client-side buttons should be
disabled. The server is already only expecting input from the current living
number of players save for confirmation pages (dead players get to look on but
can not interact).'''