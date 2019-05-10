#! /Applications/anaconda3/bin/python

from Table import Table
from Rulebook import Rulebook
from Deck import Deck
import sys

sys.tracebacklimit = 0

if __name__ == "__main__":

    #sys.stdout = open('SimulationLogs/log2.txt', 'w+')

    numplayers = 6
    bigblind = 0.02
    smallblind = 0.01
    startstack = 2.00

    realplayer = True
    playername = 'Hailey'

    numhands = 100
    #Constructor
    board = []
    rulebook = Rulebook()
    deck = Deck()
    for i in range(1,100):
        deck.shuffle()

    activetable = Table(playername, "SimTable", smallblind, bigblind, numplayers, rulebook, board, deck)

    for i in range(1,numplayers + 1):
        if realplayer and i == 1:
            activetable.add_player(playername, i, startstack, 'Realplayer')
        else:
            activetable.add_player("Player" + str(i), i, startstack)

    activetable.print_weights()
    
    for i in range(1,numhands):
        if activetable.players_left == 1:
            break
        #rotate dealer button, post blinds, and deal cards
        activetable.reset('Active')
        activetable.dealcards(not(realplayer))

        #each player does their preflop actions
        playersin = activetable.runpreflop()

        if playersin == 1:
            continue
        
        ############# FLOP ####################
        print('FLOP')
        playersin = activetable.runpostflop(3, 'Flop')

        if playersin == 1:
            continue
        
        ############# TURN ####################
        print('TURN')
        playersin = activetable.runpostflop(1, 'Turn')

        if playersin == 1:
            continue
        
        ############# RIVER ####################
        print('RIVER')
        playersin = activetable.runpostflop(1, 'River')

    pass