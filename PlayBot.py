#! /Applications/anaconda3/bin/python

import pandas as pd
import re
from Table import Table
from Rulebook import Rulebook
from Deck import Deck
from Card import Card
import sys
import statsmodels.formula.api as sm

sys.tracebacklimit = 0

if __name__ == "__main__":

    me = 'giguerefan36'
    tablename = 'RealTable'

    game_board = []
    game_rulebook = Rulebook()
    game_deck = Deck()

    #Constructor def __init__(self,myname,tablename, smallblind, bigblind, maxseats, rulebook_init, board_init, deck_init)
    activetable = Table(me,tablename, 0.01, 0.02, 6, game_rulebook, game_board, game_deck)

    totallines = 0
    table_reset = False

    while True:
        if not(table_reset):
            activetable.reset()
            table_reset = True

        if re.search('PokerStars', lines[i]) != None:
            #blind
            splitline = re.split('\$', lines[i])
            splitline2 = re.split('\s', splitline[2])
            blind = float(splitline2[0])
            #print(blind)
            i = i + 1

            #button
            splitline = re.split('#', lines[i])
            splitline2 = re.split('\s', splitline[1])
            button = int(splitline2[0])
            #print(button)
            i = i + 1
            
            #Start Pots
            while re.search('Seat', lines[i]):
                splitline = re.split('\$',lines[i])
                ## Check if player name has dollar signs
                dollarsignadd = ""
                if (len(splitline) > 2):
                    for j in range(1, len(splitline) - 1):
                        dollarsignadd += '$' + re.sub('(\s\()','',splitline[j])
                    
                splitline2 = re.split('\s', splitline[0])
                
                ## Check if player name has spaces
                if dollarsignadd == "":
                    numspaces = len(splitline2) - 4
                else:
                    numspaces = len(splitline2) - 3

                currseat = int(re.sub(':','',splitline2[1]))
                currplayer = ""
                for j in range(0,numspaces + 1):
                    if currplayer == "":
                        currplayer = splitline2[2 + j]
                    else:
                        currplayer = " ".join([currplayer, splitline2[2 + j]])
                
                currplayer = currplayer + dollarsignadd

                splitline3 = re.split('\s', splitline[len(splitline)-1])

                currstack = float(splitline3[0])
                
                activetable.add_player(currplayer, currseat, currstack)
                i = i + 1

            #posting blinds
            while re.search('Dealt', lines[i]) == None:
                if re.search('sitting out', lines[i]) != None:
                    splitline = re.split(': ', lines[i])
                    if isinstance(splitline[0], list):
                        currplayer = ": ".join(splitline[0])
                    else:
                        currplayer = splitline[0] 
                    activetable.deactivate_player(currplayer)
                i = i + 1

            #starting cards
            splitline = re.split('\[', lines[i])
            splitline2 = re.split('\s', splitline[1])

            #starting cards
            startcard1 = splitline2[0]
            startcard2 = re.sub('\]','',splitline2[1])
            i = i + 1

            ### for debug
            if (startcard1 == 'Kc' and startcard2 == '5h'):
                print("hello")

            activetable.hand_dealt(Card(startcard1), Card(startcard2))

            #print(startcard1, startcard2)

            ############################## PREFLOP #################################

            activetable.reset_turnorder_preflop(button)

            while re.search('FLOP', lines[i]) == None:
                if re.search(':', lines[i]) != None and re.search('said', lines[i]) == None:
                    splitline = re.split(': ', lines[i])
                    if isinstance(splitline[0], list):
                        currplayer = ": ".join(splitline[0])
                    else:
                        currplayer = splitline[0]
                    splitline2 = re.split('\s', splitline[1])
                    
                    ########### Regular action ###############

                    amtcall = 0.00
                    amtraise = 0.00
                    decision = splitline2[0]

                    if decision == 'calls':
                        amtcall = float(re.sub('\$','',splitline2[1]))   
                    elif decision == 'raises':
                        amtcall = activetable.calc_amountcall(currplayer)
                        amtraise = float(re.sub('\$','',splitline2[1])) 
                    elif decision == 'bets':
                        amtraise = float(re.sub('\$','',splitline2[1]))   

                    ##### Add to Preflop Dict #####
                    if currplayer == me:
                        preflop_dbdict[currid[1]] = activetable.create_db_column(amtcall + amtraise, 'preflop', currid[0], currid[1])
                        currid[1] += 1

                    activetable.newaction(currplayer, decision, amtcall, amtraise)  
                    if decision == 'folds':
                        if activetable.getplayers_in() == 1:
                            break
                else:
                    splitline = re.split('\s', lines[i])
                    currplayer = " ".join(splitline[0])
                    if re.search('leaves', lines[i]) != None:
                        numspaces = len(splitline) - 6
                        currplayer = splitline[0]
                        if numspaces > 0:
                            for j in range(1, numspaces + 1):
                                currplayer = ' '.join([currplayer, splitline[j]])
                        activetable.remove_player(currplayer)
                    elif re.search('disconnected', lines[i]) != None:
                        numspaces = len(splitline) - 5
                        currplayer = splitline[0]
                        if numspaces > 0:
                            for j in range(1, numspaces + 1):
                                currplayer = ' '.join([currplayer, splitline[j]])
                i = i + 1
            
            ############################## FLOP #################################
            
            if re.search('FLOP', lines[i]) != None:

                splitline = re.split('[\[\]]', lines[i])
                splitline2 = re.split('\s', splitline[1])
                
                flop = []
                for card_valuesuit in splitline2:
                    #print(card_valuesuit)
                    flop.append(Card(card_valuesuit))
                
                activetable.add_cards(flop)

                activetable.reset_turnorder_postflop()

                while re.search('TURN', lines[i]) == None:
                    if re.search(':', lines[i]) != None and re.search('said', lines[i]) == None:
                        splitline = re.split(': ', lines[i])
                        if isinstance(splitline[0], list):
                            currplayer = ": ".join(splitline[0])
                        else:
                            currplayer = splitline[0] 
                        splitline2 = re.split('\s', splitline[1])

                        ########### Regular action ###############

                        amtcall = 0.00
                        amtraise = 0.00
                        decision = splitline2[0]

                        if decision == 'calls':
                            amtcall = float(re.sub('\$','',splitline2[1]))   
                        elif decision == 'raises':
                            amtcall = activetable.calc_amountcall(currplayer)
                            amtraise = float(re.sub('\$','',splitline2[1])) 
                        elif decision == 'bets':
                            amtraise = float(re.sub('\$','',splitline2[1]))   

                        ##### Add to Flop Dict #####
                        if currplayer == me:
                            postflop_dbdict[currid[2]] = activetable.create_db_column(amtcall + amtraise, 'flop', currid[0], currid[2])
                            currid[2] += 1

                        activetable.newaction(currplayer, decision, amtcall, amtraise)    
                        
                        if decision == 'folds':
                            if activetable.getplayers_in() == 1:
                                break
                    else:
                        splitline = re.split('\s', lines[i])
                        currplayer = splitline[0]
                        if re.search('leaves', lines[i]) != None:
                            numspaces = len(splitline) - 6
                            currplayer = splitline[0]
                            if numspaces > 0:
                                for j in range(1, numspaces + 1):
                                    currplayer = ' '.join([currplayer, splitline[j]])
                            activetable.remove_player(currplayer)
                        elif re.search('disconnected', lines[i]) != None:
                            numspaces = len(splitline) - 5
                            currplayer = splitline[0]
                            if numspaces > 0:
                                for j in range(1, numspaces + 1):
                                    currplayer = ' '.join([currplayer, splitline[j]])
                            activetable.deactivate_player(currplayer)
                    i = i + 1
            
            ############################## TURN #################################
            
            if re.search('TURN', lines[i]) != None:

                splitline = re.split('[\[\]]', lines[i])
                #print(splitline[3])
                activetable.add_cards([Card(splitline[3])])

                activetable.reset_turnorder_postflop()

                while re.search('RIVER', lines[i]) == None:
                    if re.search(':', lines[i]) != None and re.search('said', lines[i]) == None:
                        splitline = re.split(': ', lines[i])
                        if isinstance(splitline[0], list):
                            currplayer = ": ".join(splitline[0])
                        else:
                            currplayer = splitline[0] 
                        splitline2 = re.split('\s', splitline[1])
                        
                        ########### Regular action ###############

                        amtcall = 0.00
                        amtraise = 0.00
                        decision = splitline2[0]

                        if decision == 'calls':
                            amtcall = float(re.sub('\$','',splitline2[1]))   
                        elif decision == 'raises':
                            amtcall = activetable.calc_amountcall(currplayer)
                            amtraise = float(re.sub('\$','',splitline2[1])) 
                        elif decision == 'bets':
                            amtraise = float(re.sub('\$','',splitline2[1]))   

                        ##### Add to Turn Dict #####
                        if currplayer == me:
                            postflop_dbdict[currid[2]] = activetable.create_db_column(amtcall + amtraise, 'turn', currid[0], currid[2])
                            currid[2] += 1

                        activetable.newaction(currplayer, decision, amtcall, amtraise)    
                        
                        if decision == 'folds':
                            if activetable.getplayers_in() == 1:
                                break
                    else:
                        splitline = re.split('\s', lines[i])
                        currplayer = splitline[0]
                        if re.search('leaves', lines[i]) != None:
                            numspaces = len(splitline) - 6
                            currplayer = splitline[0]
                            if numspaces > 0:
                                for j in range(1, numspaces + 1):
                                    currplayer = ' '.join([currplayer, splitline[j]])
                            activetable.remove_player(currplayer)
                        elif re.search('disconnected', lines[i]) != None:
                            numspaces = len(splitline) - 5
                            currplayer = splitline[0]
                            if numspaces > 0:
                                for j in range(1, numspaces + 1):
                                    currplayer = ' '.join([currplayer, splitline[j]])
                    i = i + 1
            
            ############################## RIVER ################################
            
            if re.search('RIVER', lines[i]) != None:
                
                splitline = re.split('[\[\]]', lines[i])
                #print(splitline[3])
                activetable.add_cards([Card(splitline[3])])

                activetable.reset_turnorder_postflop()

                while re.search('SHOW DOWN', lines[i]) == None:
                    if re.search(':', lines[i]) != None and re.search('said', lines[i]) == None:
                        splitline = re.split(': ', lines[i])
                        if isinstance(splitline[0], list):
                            currplayer = " ".join(splitline[0])
                        else:
                            currplayer = splitline[0] 
                        splitline2 = re.split('\s', splitline[1])

                        ########### Regular action ###############

                        amtcall = 0.00
                        amtraise = 0.00
                        decision = splitline2[0]

                        if decision == 'calls':
                            amtcall = float(re.sub('\$','',splitline2[1]))   
                        elif decision == 'raises':
                            amtcall = activetable.calc_amountcall(currplayer)
                            amtraise = float(re.sub('\$','',splitline2[1])) 
                        elif decision == 'bets':
                            amtraise = float(re.sub('\$','',splitline2[1]))   

                        ##### Add to Turn Dict #####
                        if currplayer == me:
                            postflop_dbdict[currid[2]] = activetable.create_db_column(amtcall + amtraise, 'river', currid[0], currid[2])
                            currid[2] += 1

                        activetable.newaction(currplayer, decision, amtcall, amtraise)    
                        
                        if decision == 'folds':
                            if activetable.getplayers_in() == 1:
                                break
                    else:
                        splitline = re.split('\s', lines[i])
                        currplayer = splitline[0]
                        if re.search('leaves', lines[i]) != None:
                            numspaces = len(splitline) - 6
                            currplayer = splitline[0]
                            if numspaces > 0:
                                for j in range(1, numspaces + 1):
                                    currplayer = ' '.join([currplayer, splitline[j]])
                            activetable.remove_player(currplayer)
                        elif re.search('disconnected', lines[i]) != None:
                            numspaces = len(splitline) - 5
                            currplayer = splitline[0]
                            if numspaces > 0:
                                for j in range(1, numspaces + 1):
                                    currplayer = ' '.join([currplayer, splitline[j]])
                    i = i + 1

            ############################## WINNERS ################################

            while re.search('SUMMARY', lines[i]) == None:
                if re.search('collected', lines[i]):
                    splitline = re.split('\s', lines[i])
                    numspaces = len(splitline) - 6
                    currplayer = splitline[0]
                    if numspaces > 0:
                        for j in range(1, numspaces + 1):
                            currplayer = ' '.join([currplayer, splitline[j]])
                    activetable.add_winner(currplayer, float(re.sub('\$', '', splitline[2 + numspaces])))
                elif re.search('returned', lines[i]):
                    splitline = re.split('\s', lines[i])
                    numspaces = len(splitline) - 7
                    currplayer = splitline[5]
                    if numspaces > 0:
                        for j in range(1, numspaces + 1):
                            currplayer = ' '.join([currplayer, splitline[j+5]])
                    activetable.newaction(currplayer, 'returned', float(re.sub('[\$\(\)]', '', splitline[2])), 0)
                i = i + 1
                
                winnings = activetable.get_winnings(me)

            
            ID_dbdict[currid[0]] = (currid[0], winnings)
            currid[0] += 1
            table_reset = False
        else:
            i = i + 1
    

    newdf = pd.DataFrame.from_dict(preflop_dbdict, orient = 'index', columns = colnames_preflop)
    preflopdb = preflopdb.append(newdf)
    newdf.to_csv('PreflopCSV/' + gamename + '.csv', index=False)
    preflopdb.to_csv('Preflop_db.csv', index = False)
    print(preflopdb)

    newdf = pd.DataFrame.from_dict(postflop_dbdict, orient = 'index', columns = colnames_postflop)
    postflopdb = postflopdb.append(newdf)
    newdf.to_csv('PostflopCSV/' + gamename + '.csv', header = colnames_postflop,index=False)
    postflopdb.to_csv('Postflop_db.csv', index = False)
    print(postflopdb)

    newdf = pd.DataFrame.from_dict(ID_dbdict, orient = 'index', columns = colnames_IDdb)
    IDdb = IDdb.append(newdf)
    IDdb.to_csv('ID_db.csv', index = False)
    print(IDdb)

    f.close()
    pass