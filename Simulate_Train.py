#! /Applications/anaconda3/bin/python

from Table import Table
from Rulebook import Rulebook
from Deck import Deck
import sys
import plotly.plotly as py
import plotly.tools as tls
import plotly.graph_objs as go
import plotly.io as pio
import pandas as pd
import random
import re
import numpy as np


def loadlast_iteration(filepath, numpreflop_layers, numpostflop_layers, *argv):
    f = open(filepath)
    lines = f.readlines()
    preflopweights = []
    postflopweights = []
    
    currline = 0

    for i in range(0, 6):
        currpreflopweights = []
        #### preflop weights #####
        for j in range(0, numpreflop_layers):
            currlayer = []
            for k in range(0, argv[j][0]):
                splitline = re.sub('[\[\]\n]', '', lines[currline])
                splitline2 = re.split('\s', splitline)
                splitline2 = filter(None, splitline2)
                currlayer.append(list(map(lambda x: float(x), splitline2)))
                currline += 1
        
            np_currprefloplayer = np.array(currlayer)
            currpreflopweights.append(np_currprefloplayer)
        
        preflopweights.append(currpreflopweights)

        currpostflopweights = []
        #### postflop weights #####
        for j in range(0, numpostflop_layers):
            currlayer = []
            for k in range(0, argv[j + numpreflop_layers][0]):
                splitline = re.sub('[\[\]\n]', '', lines[currline])
                splitline2 = re.split('\s', splitline)
                splitline2 = filter(None, splitline2)
                currlayer.append(list(map(lambda x: float(x), splitline2)))
                currline += 1
        
            np_currpostfloplayer = np.array(currlayer)
            currpostflopweights.append(np_currpostfloplayer)
        
        postflopweights.append(currpostflopweights)
   
    
    winnerslist = list(map(lambda x: int(x) - 1, re.split(', ', re.sub('[(Player)\n]', '', lines[-1]))))
    return (preflopweights[winnerslist[0]], postflopweights[winnerslist[0]],
    preflopweights[winnerslist[1]], postflopweights[winnerslist[1]])





sys.tracebacklimit = 0

if __name__ == "__main__":
    original = sys.stdout

    numplayers = 6
    bigblind = 0.02
    smallblind = 0.01
    startstack = 2.00

    realplayer = False
    playername = 'Bailey'
    numrealplayers = 6

    resume_previous = False
    exhibittail = 'NN-Converge_20_pt2'

    numhands = 300
    numgenerations = 10000

    convergence_age = 20

    #Constructor
    board = []
    rulebook = Rulebook()
    deck = Deck()
    for i in range(1,100):
        deck.shuffle()

    preflopweights = {}
    postflopweights = {}
    preflopweights2 = {}
    postflopweights2 = {}
    winningstack={}
    winningstack2={}
    gamelengths={}

    activetable = Table(playername, "SimTable", smallblind, bigblind, numplayers, rulebook, board, deck)

    preflop_colnames = ('High_card','Kicker','NumIn','Pocket','Suited', 'PotInvestment', 'AmountToCall')
    postflop_colnames = ('Street', 'Hand', 'Outs', 'PotInvestment', 'AmountToCall', 'NumCalls', 'Bankroll')


    for i in range(1,numplayers + 1):
        if realplayer and i <= numrealplayers:
            print("Player" + str(i) + " name:")
            currplayername = sys.stdin.readline()
            activetable.add_player(currplayername, i, startstack, 'Realplayer')
        else:
            activetable.add_player("Player" + str(i), i, startstack)


    ### Resume previous simulation
    lastlognumber = 0

    if resume_previous:
        lastlognumber = 20100
        lastlog = 'SimulationLogsNN/log' + str(lastlognumber) + '.txt'
        lastweights = loadlast_iteration(lastlog, 2, 2, (7,2), (2, 3), (7, 2), (2, 3))

        activetable.adjustweights((lastweights[0], lastweights[1]), (lastweights[2], lastweights[3]))

    generation = lastlognumber

    #for currgeneration in range(0, numgenerations):
    while True:
        max_age_tuple = activetable.get_max_age()
        if max_age_tuple[1] > convergence_age:
            break
        generation += 1
        sys.stdout = open('SimulationLogsConvergence_20_pt2/log' + str(generation) + '.txt', 'w+')
        activetable.print_weights()
        print(max_age_tuple)
        totalhands = 0

        for i in range(1,numhands):
            print ('************** HAND ' + str(i) + '*************')
            if activetable.players_left() <= 2:
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

        activetable.reset('Active')
        ##### Keep only top 2 players ######
        top2 = activetable.return_top2_players()

        ##### Track Game Length ####
        totalhands = i
        gamelengths[generation] = totalhands

        ##### track top2 player data #####
        #preflopweights[generation] = list(np.transpose(activetable.get_preflop_weights(top2[0])[0])[0])
        #postflopweights[generation] = list(np.transpose(activetable.get_postflop_weights(top2[0])[0])[0])

        #preflopweights2[generation] = list(np.transpose(activetable.get_preflop_weights(top2[1])[0])[0])
        #postflopweights2[generation] = list(np.transpose(activetable.get_postflop_weights(top2[1])[0])[0])

        #### track top2 player stack #####
        winningstack[generation] = activetable.get_stack(top2[0])
        winningstack2[generation] = activetable.get_stack(top2[1])

        activetable.breednewplayers()
        sys.stdout.close()
        sys.stdout = original
        print('******* Game' + str(generation) + ' Complete *********')

    preflopweights_df = pd.DataFrame.from_dict(preflopweights, orient = 'index', columns = preflop_colnames)
    postflopweights_df = pd.DataFrame.from_dict(postflopweights, orient = 'index', columns = postflop_colnames)
    
    gamelength_df = pd.DataFrame.from_dict(gamelengths, orient= 'index', columns = ['Gamelengths'])
    winningstack_df = pd.DataFrame.from_dict(winningstack, orient = 'index', columns = ['Winningstack'])
    winningstack_df2 = pd.DataFrame.from_dict(winningstack2, orient = 'index', columns = ['Winningstack2'])

    ########################################### Game Length Analysis ###########################################
    gamelength_traces = []
    gamelength_traces.append(
        go.Scatter(
            x = list(gamelengths.keys()),
            y = list(gamelength_df.loc[:,'Gamelengths'].values),
            mode = "lines+markers",
            name = 'Game Lengths',
            marker = dict(color = 'rgba(255, 182, 193, .9)')    
        )
    )

    layout = dict(
        title = 'Game Lengths per generation',
        yaxis = dict(zeroline = False),
        xaxis = dict(zeroline = False)
    )

    fig = dict(data = gamelength_traces)
    pio.write_image(fig, 'Figures/GameLengths' + exhibittail + '.png')


    ########################################### Stack Sizes Analysis ###########################################
    winningstack_traces = []
    winningstack_traces.append(
        go.Scatter(
            x = list(winningstack.keys()),
            y = list(winningstack_df.loc[:,'Winningstack'].values),
            mode = "lines+markers",
            name = 'Winning Stack',
            marker = dict(color = 'rgba(255, 182, 193, .9)')    
        )
    )

    winningstack_traces.append(
        go.Scatter(
            x = list(winningstack2.keys()),
            y = list(winningstack_df2.loc[:,'Winningstack2'].values),
            mode = "lines+markers",
            name = 'Second Stack',
            marker = dict(color = 'rgba(152, 0, 0, .8)')    
        )
    )

    layout = dict(
        title = 'Winning stacks per generation',
        yaxis = dict(zeroline = False),
        xaxis = dict(zeroline = False)
    )

    fig = dict(data = winningstack_traces)
    pio.write_image(fig, 'Figures/StackSizes' + exhibittail + '.png')

    # ########################################### Preflop Weights Analysis ###########################################
    # prefloptraces = []

    # for i in range(0, 7):
    #     r = str(random.randint(0, 255)) + ','
    #     g = str(random.randint(0, 255)) + ','
    #     b = str(random.randint(0, 255)) + ','
    #     prefloptraces.append(
    #         go.Scatter(
    #             x = list(preflopweights.keys()),
    #             y = list(preflopweights_df.loc[:,preflop_colnames[i]].values),
    #             mode = "lines+markers",
    #             name = preflop_colnames[i],
    #             marker = dict(color = 'rgba(' + r + g + b + '0.8)')

    #     ))

    # layout = dict(
    #     title = 'Preflop Weights per Generation',
    #     yaxis = dict(zeroline = False),
    #     xaxis = dict(zeroline = False)
    # )

    # fig = dict(data = prefloptraces, layout = layout)
    # pio.write_image(fig, 'Figures/PreflopWeights' + exhibittail + '.png')

    # ########################################### Postflop Weights Analysis ###########################################
    # postfloptraces = []

    # for i in range(0, 7):
    #     r = str(random.randint(0, 255)) + ','
    #     g = str(random.randint(0, 255)) + ','
    #     b = str(random.randint(0, 255)) + ','
    #     postfloptraces.append(
    #         go.Scatter(
    #             x = list(postflopweights.keys()),
    #             y = list(postflopweights_df.loc[:,postflop_colnames[i]].values),
    #             mode = "lines+markers",
    #             name = postflop_colnames[i],
    #             marker = dict(color = 'rgba(' + r + g + b + '0.8)')

    #     ))

    # layout = dict(
    #     title = 'Postflop Weights per Generation',
    #     yaxis = dict(zeroline = False),
    #     xaxis = dict(zeroline = False)
    # )

    # fig = dict(data = postfloptraces, layout = layout)
    # pio.write_image(fig, 'Figures/PostflopWeights' + exhibittail + '.png')


    pass