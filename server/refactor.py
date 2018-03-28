





def setup(request, confirm=0, playerCount=0):
    """Initial setup call. Received from activity_main.xml or activity_end.xml,
    this checks if a game is already in progress (requires confirmation 
    [confirm=1]) to overwrite game in progress), clears all databases, and
    initializes the GameState object and sets the statusID to 2 (accepting 
    players). Returns HttpResponses 'confirm' 'override.'"""

    def getResources(num):
        Player.objects.all().delete()
        GameState.objects.all().delete()
        Voting.objects.all().delete()
        PresidentQueue.objects.all().delete()
        PolicyDeck.objects.all().delete()
        DiscardPile.objects.all().delete()
        G = GameState(libPolicyCount=0, fasPolicyCount=0, electionTracker=0, 
                      statusID=1, numberOfPlayers=num, chancellorNominated="",
                      EX_AffiliationCheckOccurred1=False, EX_AffiliationCheckOccurred2=False,
                      EX_SpecialElectionCalled=False, EX_PolicyPeekDone=False,
                      EX_Exection1=False, EX_Exection2=False,
                      statusUpdate="Waiting for players to join...", lastPolicyPassed="")
        G.save()
        updateGStatusID(2)
        return

    if not len(Player.objects.all()) == 0:
        if confirm:
            getResources(playerCount)
            return HttpResponse('confirm')
        else:
            return HttpResponse("override")
    else:
        getResources(playerCount)
        return HttpResponse('confirm')

def finalizeResources():
    setUpMatch()
    logging.info("start(): setUpMatch() run.")
    setUpPolicyDeck()
    logging.info("start(): setUpPolicyDeck() run.")
    setUpPresidentQueue()
    logging.info("start(): setUpPresidentQueue() run.")
    updateGStatusID(3)
    updateGStatusUpdate(f"Game has started. {findCurrentPresident().name} is now President.")
    return



def getStatus(id):
    """Function that pulls requesting player's name, party, role, the
    GameState.statusID, and GameState.statusUdpdate. Also includes secret
    information for Fascist players. Packaged in JsonResponse object."""
    G = GameState.objects.all()[0]
    P = Player.objects.get(pk=id)
    information = {}
    information["name"] = P.name
    information["name"] = P.name
    information["party"] = P.party
    information["role"] = P.role
    information["statusID"] = G.statusID
    information["statusUpdate"] = G.statusUpdate
    if P.role == "Liberal":
        return JsonResponse(information)
    elif P.role == "Hitler":
        if G.numberOfPlayers == 5 or G.numberOfPlayers == 6:
            for i in Player.objects.all():
                if i.party == "Fascist":
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

def votingFinished():
    V = Voting.objects.all()
    G = GameState.objects.all()[0]
    P = Player.objects.all()
    logging.info("---------------------------")
    logging.info("Voting completed.")
    logging.info("---------------------------")
    if votingTally():
        currentChanceller = findCurrentChancellor()
        if currentChanceller != None:
            currentChanceller.chancellor = False
            currentChanceller.save()
        newChancerllor = Player.objects.get(pk=findPlayerID(G.chancellorNominated))
        newChancerllor.chancellor = True
        lastPresident = findCurrentPresident()
        lastPresident.previousPresident = True
        lastPresident.president = False
        G.chancellorNominated = ""
        G.save(), lastPresident.save(), newChancerllor.save()
        updateGStatusID(99) # Changing to statusID 99 (vote passed)
        updateGStatusUpdate(f"Vote passed. President {findCurrentPresident(True).name} \
            and Chancellor {findCurrentChancellor().name} will now enact a policy decision.")
        cyclePresident() 
        '''Cycling the presidency now because findCurrentPresident(post=True) 
        should prevent bugs where the upcoming president gets current 
        policy-enacting president's powers/views/etc.'''
        Voting.objects.all().delete()
        # return policyHandling(request)
        return
    else:
        updateGStatusUpdate("The election has failed. The election tracker will increase by 1.")
        updateElectionTracker()
        G.chancellorNominated = ""
        if G.electionTracker >= 3:
            x = electionTrackerFull()
            updateGStatusUpdate(G.statusUpdate + " The people have enacted a {0} policy!".format(x))
        updateGStatusID(98) # Changing to statusID 98 (vote failed)
        G.save()
        Voting.objects.all().delete()
        cyclePresident()
        '''Cycling the presidency now because findCurrentPresident(post=True) 
        should prevent bugs where the upcoming president gets current 
        policy-enacting president's powers/views/etc.'''
        # return base(request)
        return

