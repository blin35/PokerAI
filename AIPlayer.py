#! /Applications/anaconda3/bin/python

from PIL import Image
import random as random
import itertools
import pyautogui as pyautogui
import pytesseract
import re
import sys
from Table import Table
from Rulebook import Rulebook
from Deck import Deck
from Card import Card

if __name__ == "__main__":
    
    playerlocations = [(1600,980), (976, 915), (976, 569), (1600, 410), (1925, 569), (1925, 915)]
    player_activelocations = [(1705, 1137), (1115, 944), (1115, 600), (1700, 467), (2297, 600), (2300, 944)]
    playersizes = [(360, 300), (635, 300), (635, 300), (360, 300), (653, 300), (635, 300)]

    playernames = []

    ############### Step 1: Initialize Identification Variables ##########
    baseimage = Image.open('./Screenshots/67.png')
    activepixel = baseimage.getpixel((2303, 941))
    whitepixel = baseimage.getpixel((1521, 850))
    baseimage.close()


    ############### Step 2: Create Game ##########

    original = sys.stdout

    numplayers = 6
    bigblind = 0.02
    smallblind = 0.01
    startstack = 2.00

    realplayer = False
    playername = 'giguerefan'
    numrealplayers = 6
    player_in = [realplayer, True, True, True, True, True]

    board = [(1504, 767), (1612, 767), (1720, 767), (1828, 767), (1936, 767)]
    card_dimensions = (96, 80)
    whitepixels = [(1521, 848), (1629, 848), (1737, 848), (1845, 848), (1953, 848)]

    chatbox = (980, 1326, 1685, 1440)

    resume_previous = False

    board = []
    rulebook = Rulebook()
    deck = Deck()

    activetable = Table(playername, "TestTable", smallblind, bigblind, numplayers, rulebook, board, deck)

    ############# Wait until New Hand Starts ############
    curr_state = pyautogui.screenshot()
    for i in range(0, 6):
        cropped = curr_state.crop((playerlocations[i][0], playerlocations[i][1], playerlocations[i][0] + playersizes[i][0], playerlocations[i][1] + playersizes[i][1]))
        text = pytesseract.image_to_string(cropped, lang = 'eng')
        if re.search('TAKE SEAT', text) != None and re.search('Sitting Out', text) != None:
            player_in = False
            playernames.append('None')
        else:
            playernames.append(re.split('/n', text)[0])


    while True:
        numplayers = player_in.count(True)

        curr_state = pyautogui.screenshot()
        activeplayers = 0
        for x, y in player_activelocations:
            if curr_state.getpixel((x, y)) == activepixel:
                activeplayer += 1

        #### initialize players #####
        if activeplayers == numplayers:
            for i in range(1, 7):
                if player_in[i -1]:
                    activetable.add_player(playernames[i-1], i, 2.00)
            break
    
    ########################## Start Game ###############################
    game_state = 'Preflop'
    playernames = {}
    
    while True:
        curr_state = pyautogui.screenshot()
        if not(table_reset):
            activetable.reset()
            table_reset = True
         
         ############################## PREFLOP ############################
        if game_state == 'Preflop':
            maxraise = bigblind

            # stacks, blinds, and new players
            for i in range(0, 6):
                cropped = curr_state.crop((playerlocations[i][0], playerlocations[i][1], playerlocations[i][0] + playersizes[i][0], playerlocations[i][1] + playersizes[i][1]))
                text = pytesseract.image_to_string(cropped, lang = 'eng')
                if re.search('TAKE SEAT', text) != None and re.search('Sitting Out', text) != None:
                    splitline = re.split('/n', text)
                    playername = splitline[0]
                    playernames[i] = playername
                    if len(splitline) > 3:
                        stack_size = float(re.sub('/$', '', splitline[1])) + float(re.sub('/$', '', splitline[2]))
                    else:
                        stack_size = float(re.sub('/$', '', splitline[1]))   
                    activetable.add_player(playername, i, stack_size)

            # button
            buttonlocation = pyautogui.locateOnScreen('Button.png')
            for i in range(0, 6):
                if (buttonlocation[0] >= playerlocations[i][0] 
                    and buttonlocation[0] <= playerlocations[i][0] + playersizes[i][0]
                    and buttonlocation[1] >= playerlocations[i][1]
                    and buttonlocation[1] <= playerlocations[i][1] + playersizes[i][1]):
                    activetable.reset_turnorder_preflop(i)
                    break
            

            ########## Preflop Actions ############
            while curr_state.getpixel(whitepixels[0]) != whitepixel:
                activeplayer = activetable.whose_turn()
                if activetable.getplayers_in() == 1:
                    activetable.add_winner(playernames[activeplayer])
                    break
                while True:
                    curr_state = pyautogui.screenshot()
                    if curr_state.getpixel(whitepixels[0]) == whitepixel:
                        game_state = 'Flop'
                        break
                    croppedplayer = curr_state.crop((playerlocations[activeplayer][0], 
                        playerlocations[activeplayer][1], 
                        playerlocations[activeplayer][0] + playersizes[activeplayer][0],
                        playerlocations[activeplayer][1] + playersizes[activeplayer][1]))
                    splitline = re.split('/n', pytesseract.image_to_string(croppedplayer, lang = 'eng'))
                    decision = splitline[0]
                    amtcall = 0
                    amtraise =  0
                    if decision != playernames[activeplayer]:
                        if decision == 'Call':
                            decision = 'calls'
                            amtcall = activetable.calc_amountcall(playernames[activeplayer])
                        elif decision == 'Bet':
                            decision = 'bets'
                            amtraise = float(re.sub('/$', '', splitline[2]))
                        elif decision == 'Raise':
                            decision = 'raises'
                            amtcall = activetable.calc_amountcall(playernames[activeplayer])
                            amtraise = float(re.sub('/$', '', splitline[2]) - maxraise)
                            maxraise = float(re.sub('/$', '', splitline[2]))
                        elif decision == 'Folds':
                            decision = 'folds'
                        elif decision == 'Checks':
                            decision = 'checks'
                    
                    activetable.newaction(playernames[activeplayer], decision, amtcall, amtraise)
                    break


        ############################### FLOP ############################
        elif game_state == 'Flop':
            maxraise = 0
            activetable.reset_turnorder_postflop()

            ########## Flop Actions ############
            while curr_state.getpixel(whitepixels[3]) != whitepixel:
                while curr_state.getpixel(whitepixels[2]) != whitepixel:
                    curr_state = pyautogui.screenshot()
                ##### Identify Flop Cards ######
                    for i in range(0, 3):
                        card = curr_state.crop((board[i][0], board[i][1], board[i][0] + card_dimensions[0], board[i][1] + card_dimensions[1]))
                        value = pytesseract.image_to_string(card, lang = 'Eng')
                        if value =='10':
                            value = 'T'
                        suit = 's'
                        activetable.add_cards([Card(value + suit)])
                    
                activeplayer = activetable.whose_turn()
                if activetable.getplayers_in() == 1:
                    activetable.add_winner(playernames[activeplayer])                    
                    break
                while True:
                    curr_state = pyautogui.screenshot()
                    if curr_state.getpixel(whitepixels[3]) == whitepixel:
                        game_state = 'Turn'
                        break
                    croppedplayer = curr_state.crop((playerlocations[activeplayer][0], 
                        playerlocations[activeplayer][1], 
                        playerlocations[activeplayer][0] + playersizes[activeplayer][0],
                        playerlocations[activeplayer][1] + playersizes[activeplayer][1]))
                    splitline = re.split('/n', pytesseract.image_to_string(croppedplayer, lang = 'eng'))
                    decision = splitline[0]
                    amtcall = 0
                    amtraise =  0
                    if decision != playernames[activeplayer]:
                        if decision == 'Call':
                            decision = 'calls'
                            amtcall = activetable.calc_amountcall(playernames[activeplayer])
                        elif decision == 'Bet':
                            decision = 'bets'
                            amtraise = float(re.sub('/$', '', splitline[2]))
                        elif decision == 'Raise':
                            decision = 'raises'
                            amtcall = activetable.calc_amountcall(playernames[activeplayer])
                            amtraise = float(re.sub('/$', '', splitline[2]) - maxraise)
                            maxraise = float(re.sub('/$', '', splitline[2]))
                        elif decision == 'Folds':
                            decision = 'folds'
                        elif decision == 'Checks':
                            decision = 'checks'
                    
                    activetable.newaction(playernames[activeplayer], decision, amtcall, amtraise)
                    break

############################### TURN ############################
        elif game_state == 'Turn':
            maxraise = 0
            activetable.reset_turnorder_postflop()

            ########## Turn Actions ############
            while curr_state.getpixel(whitepixels[4]) != whitepixel:
                ##### Identify Turn Cards ######
                card = curr_state.crop((board[3][0], board[3][1], board[3][0] + card_dimensions[0], board[3][1] + card_dimensions[1]))
                value = pytesseract.image_to_string(card, lang = 'Eng')
                if value =='10':
                    value = 'T'
                suit = 's'
                activetable.add_cards([Card(value + suit)])
            
                activeplayer = activetable.whose_turn()
                if activetable.getplayers_in() == 1:
                    activetable.add_winner(playernames[activeplayer])                    
                    break
                while True:
                    curr_state = pyautogui.screenshot()
                    if curr_state.getpixel(whitepixels[0]) == whitepixel:
                        game_state = 'River'
                        break
                    croppedplayer = curr_state.crop((playerlocations[activeplayer][0], 
                        playerlocations[activeplayer][1], 
                        playerlocations[activeplayer][0] + playersizes[activeplayer][0],
                        playerlocations[activeplayer][1] + playersizes[activeplayer][1]))
                    splitline = re.split('/n', pytesseract.image_to_string(croppedplayer, lang = 'eng'))
                    decision = splitline[0]
                    amtcall = 0
                    amtraise =  0
                    if decision != playernames[activeplayer]:
                        if decision == 'Call':
                            decision = 'calls'
                            amtcall = activetable.calc_amountcall(playernames[activeplayer])
                        elif decision == 'Bet':
                            decision = 'bets'
                            amtraise = float(re.sub('/$', '', splitline[2]))
                        elif decision == 'Raise':
                            decision = 'raises'
                            amtcall = activetable.calc_amountcall(playernames[activeplayer])
                            amtraise = float(re.sub('/$', '', splitline[2]) - maxraise)
                            maxraise = float(re.sub('/$', '', splitline[2]))
                        elif decision == 'Folds':
                            decision = 'folds'
                        elif decision == 'Checks':
                            decision = 'checks'
                    
                    activetable.newaction(playernames[activeplayer], decision, amtcall, amtraise)
                    break

############################### RIVER ############################
        elif game_state == 'River':
            maxraise = 0
            activetable.reset_turnorder_postflop()

            ########## River Actions ############
            while curr_state.getpixel(whitepixels[4]) == whitepixel:
                ##### Identify River Cards ######
                card = curr_state.crop((board[4][0], board[4][1], board[4][0] + card_dimensions[0], board[4][1] + card_dimensions[1]))
                value = pytesseract.image_to_string(card, lang = 'Eng')
                if value =='10':
                    value = 'T'
                suit = 's'
                activetable.add_cards([Card(value + suit)])
            
                activeplayer = activetable.whose_turn()
                if activetable.getplayers_in() == 1:
                    activetable.distribute_winnings([playernames[activeplayer], activeplayer])
                    break
                while True:
                    if curr_state.getpixel(whitepixels[0]) != whitepixel:
                        game_state = 'Prelop'
                        while True:
                            curr_state = pyautogui.screenshot()
                            chat = curr_state.crop(chatbox)
                            chat_text = pytesseract.image_to_string(chat, lang='Eng')
                            splitline = re.split('/n', chat_text)
                            last_2_lines = ' '.join([splitline[2], splitline[3]])
                            if re.search('Dealer: Hand #', last_2_lines) != None:
                                winstring = re.split(': ', last_2_lines)[1]
                                if re.search('wins', winstring) != None:
                                    winner = re.split(' wins', winstring)[0]
                                    activetable.add_winner(winner)
                                    break
                                elif re.search('ties', winstring) != None:
                                    activetable.splitpot()
                                    break
                                    
                        break
                    croppedplayer = curr_state.crop((playerlocations[activeplayer][0], 
                        playerlocations[activeplayer][1], 
                        playerlocations[activeplayer][0] + playersizes[activeplayer][0],
                        playerlocations[activeplayer][1] + playersizes[activeplayer][1]))
                    splitline = re.split('/n', pytesseract.image_to_string(croppedplayer, lang = 'eng'))
                    decision = splitline[0]
                    amtcall = 0
                    amtraise =  0
                    if decision != playernames[activeplayer]:
                        if decision == 'Call':
                            decision = 'calls'
                            amtcall = activetable.calc_amountcall(playernames[activeplayer])
                        elif decision == 'Bet':
                            decision = 'bets'
                            amtraise = float(re.sub('/$', '', splitline[2]))
                        elif decision == 'Raise':
                            decision = 'raises'
                            amtcall = activetable.calc_amountcall(playernames[activeplayer])
                            amtraise = float(re.sub('/$', '', splitline[2]) - maxraise)
                            maxraise = float(re.sub('/$', '', splitline[2]))
                        elif decision == 'Folds':
                            decision = 'folds'
                        elif decision == 'Checks':
                            decision = 'checks'
                    
                    activetable.newaction(playernames[activeplayer], decision, amtcall, amtraise)
                    break

                if activetable.getplayers_in() > 1:
                    game_state = 'River'




