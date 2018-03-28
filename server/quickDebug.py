from .models import Player, GameState, Voting, Confirmation, PolicyDeck, DiscardPile, PresidentQueue

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
    return True

if __name__ == '__main__':
    mockData1()