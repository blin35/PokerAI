#! /Applications/anaconda3/bin/python
from Card import Card
from Rulebook import Rulebook
import random as rand
import numpy as np
import sys
import re

####################### Neural Network #############################
def sigmoid(x, derivative=False):
        return x*(1-x) if derivative else 1/(1+np.exp(-x))


class Player:
    def __init__(self, name, seat, stack, rulebook, board, playertype, randomweights = True, preflopweights = [], postflopweights = []):
        self.status = 'Active'
        self.call_status = 'Uncalled'
        self.type = playertype
        self.name = name
        self.seat = seat
        self.age = 0
        self.stack = stack
        self.position = 0
        self.allactions = {}
        self.currentactions = []
        self.current_hand = []
        self.board = board
        self.allouts = 0
        self.handvalue = 0
        self.total_potinvestment = 0.00
        self.current_potinvestment = 0.00
        self.splitpot = 0.00

        ###################### Linear Regression #########################

        if randomweights:
            self.preflop_weights = np.random.uniform(low = -4, high = 4, size = (7, 1))
            self.postflop_weights = np.random.uniform(low = -4, high = 4, size = (7, 1))
        else:
            self.preflop_weights = preflopweights[0]
            self.postflop_weights = postflopweights[0]

        ###################### Neural Net #########################

        # self.preflop_weights = np.random.uniform(low = -1, high = 1, size = (7, 2))
        # self.postflop_weights = np.random.uniform(low = -1, high = 1, size = (7, 2))
        # self.preflop_weights2 = np.random.uniform(low = -1, high = 1, size = (2, 3))
        # self.postflop_weights2 = np.random.uniform(low = -1, high = 1, size = (2, 3))

        ###################### New Method #########################

        self.handsplayed = 1
        self.handswon = 0
        self.rulebook = rulebook
    
    def get_stack(self):
        return self.stack
    
    def get_hand(self):
        return self.current_hand
    
    def getstatus(self):
        return self.status
    
    def get_age(self):
        return self.age

    def add_age(self):
        self.age += 1
    
    def deactivate(self):
        self.status = 'Inactive'
    
    def activate(self):
        self.status = 'Active'
    
    def allin(self):
        self.status = 'All-In'
    
    def getseat(self):
        return self.seat
    
    def get_preflop_weights(self):
        ########### Linear Regression ##############
        return [self.preflop_weights]
        ########### Neural Network ##############
        #return (self.preflop_weights, self.preflop_weights2)
    
    def get_postflop_weights(self):
        ########### Linear Regression ##############
        return [self.postflop_weights]
        ########### Neural Network ##############
        #return (self.preflop_weights, self.preflop_weights2)

    def getpotinvestment(self):
        return self.total_potinvestment + self.current_potinvestment
    
    def get_currentpotinvestment(self):
        return self.current_potinvestment

    def updatestack(self,currstack):
        self.stack = currstack
    
    def updateseat(self, newseat):
        self.seat = newseat
    
    def updatename(self, newname):
        self.name = newname

    def updateposition(self,currposition):
        self.position = currposition
    
    def reset(self, status):
        self.status = status
        self.position = 0
        self.total_potinvestment = 0
        self.current_potinvestment = 0
        self.splitpot = 0
        self.allactions[self.handsplayed] = self.currentactions
        self.currentactions = []
        self.handsplayed += 1
        self.current_hand = []
        self.stack = round(self.stack, 2)

    def addaction(self, newaction, amount):
        if newaction == 'folds':
            self.currentactions.append(('folds', round(amount - self.current_potinvestment, 2)))
        elif newaction == 'returned':
            self.current_potinvestment -= amount
        elif newaction == 'calls':
            self.currentactions.append(('calls', amount))
            self.makearaise(amount)
        elif newaction == 'raises' or newaction == 'bets':
            self.currentactions.append((newaction, amount))
            self.makearaise(amount)
        else:
            self.currentactions.append(('checks', 0))
    
    def listcurrentactions(self):
        custom = lambda x: '_'.join(map(str,x))
        currentactionslist = '_'.join(map(custom,self.currentactions))
        return currentactionslist

    def makearaise(self, amount):
        #if self.stack > amount:
        self.current_potinvestment += amount
        self.stack -= amount
        self.current_potinvestment = round(self.current_potinvestment, 2)
        self.stack = round(self.stack, 2)
        if self.stack < 0.01:
            self.status = 'All-In'
        return amount
        # else:
        #     amount_paid = self.stack
        #     self.current_potinvestment += self.stack
        #     self.stack = 0.00
        #     self.status = 'All-In'
        #     return amount_paid

    def add_win(self, winnings):
        self.handswon += 1
        self.total_potinvestment -= winnings
    
    def new_street(self):
        self.total_potinvestment += self.current_potinvestment
        self.current_potinvestment = 0
    
    def new_hand(self, card1, card2, printhand):
        self.stack = round(self.stack, 2)
        self.current_hand.append(card1)
        self.current_hand.append(card2)
        print(self.name + " " + str(self.stack))
        if printhand or self.type != 'Computer':
            print(card1.get_value() + card1.get_suit() + " " + card2.get_value() + card2.get_suit())

    def get_regression_params(self, actionvalue, maxraise, playersin, street, blind, hand_id, row_id):
        
        if street == "preflop":
            pocket = False
            suited = False
            if self.current_hand[0].get_value() == self.current_hand[1].get_value():
                pocket = True
            if self.current_hand[0].get_suit() == self.current_hand[1].get_suit():
                suited = True
            return  (row_id, actionvalue/blind, self.rulebook.gethighcard(self.current_hand), self.rulebook.getkicker(self.current_hand),
                playersin, pocket, suited, round((self.total_potinvestment + self.current_potinvestment)/blind, 1), round((maxraise - self.current_potinvestment)/blind, 1), hand_id)
        else:
            if street == "flop":
                streetnum = 1
            elif street == "turn":
                streetnum = 2
            else:
                streetnum = 3
            handvalue = self.rulebook.calc_hand(self.current_hand, self.board)
            boardvalue = self.rulebook.calc_hand([], self.board)[0]
            truehandvalue = (handvalue[0] - boardvalue)/14**5
            return  (row_id, actionvalue/blind, streetnum, truehandvalue, handvalue[1],
                round((self.total_potinvestment + self.current_potinvestment)/blind, 1), round((maxraise - self.current_potinvestment)/blind, 1), playersin, round(self.stack/blind, 2), hand_id)

    ################ Simulation ########################
    def add_win_sim(self, winnings):
        print(self.name + " Won " + str(winnings))
        self.handswon += 1
        self.total_potinvestment -= winnings
        self.stack += winnings

    def new_action(self, maxraise, playersin, street, blind):
        action = ''
        amtcall = 0.00
        amtraise = 0.00
        if self.type == 'Computer' and self.status != 'All-In': 
            ############## Use AI Algorithm ####################
            if street == "Preflop":
                pocket = False
                suited = False
                if self.current_hand[0].get_value() == self.current_hand[1].get_value():
                    pocket = True
                if self.current_hand[0].get_suit() == self.current_hand[1].get_suit():
                    suited = True
                xvals = (self.rulebook.gethighcard(self.current_hand), self.rulebook.getkicker(self.current_hand),
                    playersin, pocket, suited, round((self.total_potinvestment + self.current_potinvestment)/blind, 1), round((maxraise - self.current_potinvestment)/blind, 1))
                decisionvalue = np.dot(xvals, self.preflop_weights)
            else:
                streets = ['Flop', 'Turn', 'River']
                handvalue = self.rulebook.calc_hand(self.current_hand, self.board)
                boardvalue = self.rulebook.calc_hand([], self.board)[0]
                truehandvalue = (handvalue[0] - boardvalue)/14**5
                xvals = (truehandvalue, handvalue[1],
                    round((self.total_potinvestment + self.current_potinvestment)/blind, 1), round((maxraise - self.current_potinvestment)/blind, 1), playersin, round(self.stack/blind, 2), streets.index(street))
                
        ##################### Linear Regression #####################
                decisionvalue = np.dot(xvals, self.postflop_weights)
        
        ##################### Neural Net #####################
            #     layer1 = sigmoid(np.dot(xvals, self.preflop_weights))
            #     decisionmatrix = sigmoid(np.dot(layer1, self.preflop_weights2))

            # decisionvalue = max(decisionmatrix)
        
        ##################### Neural Net #####################

            if decisionvalue <= 1:
                if maxraise - self.current_potinvestment == 0.00:
                    action = 'checks'
                    amtcall = 0.00
                    amtraise = 0.00
                    print(self.name + " " + action)
                else:
                    action = 'folds'
                    amtcall = 0.00
                    amtraise = 0.00
                    print(self.name + " " + action)
            elif decisionvalue >= 4:
                if maxraise == 0.00:
                    action = 'bets'
                    amtcall = 0.00
                    amtraise = round(min(rand.randint(2, 4)/100, self.stack), 2)
                    print(self.name + " " + action + " " + str(amtraise))
                else:
                    action = 'calls'
                    amtcall = round(min(maxraise - self.current_potinvestment, self.stack), 2)
                    if amtcall == 0.00:
                        action = 'checks'
                        print(self.name + " " + action)
                    else:
                        print(self.name + " " + action + " " + str(amtcall))

            else:
                if maxraise == 0.00:
                    action = 'bets'
                    amtcall = 0.00
                    amtraise = round(min(rand.randint(2, 4)/100, self.stack), 2)
                    print(self.name + " " + action + " " + str(amtraise))
                else:
                    action = 'raises'
                    amtcall = round(min(maxraise - self.current_potinvestment, self.stack), 2)
                    if amtcall == self.stack:
                        action = 'calls'
                        amtraise = 0.00
                        print(self.name + " " + action + " " + str(amtcall))
                    else:
                        amtraise = round(min(self.stack - amtcall, maxraise), 2)
                        print(self.name + " " + action + " " + str(amtraise))
            
            ##################### Linear Regression #####################

            amtcall = round(amtcall, 2)
            amtraise = round(amtraise, 2)

            if amtcall + amtraise == self.stack:
                print(self.name + ' is All-In')
        else:
            ############## Real Player ####################
            print("********* YOUR TURN ***************")
            validaction = False
            if (maxraise - self.current_potinvestment) > 0:
                validactions = ['calls', 'raises', 'folds']
            elif self.current_potinvestment > 0:
                validactions = ['raises', 'checks', 'folds']
            else:
                validactions = ['bets', 'checks', 'folds']
            print('valid actions')
            print(validactions)
            while not(validaction):
                actionstring = sys.stdin.readline()
                actionstring_split = re.split('/s', actionstring)
                action = re.sub('\n', '', actionstring_split[0])
                if action in validactions:
                    validaction = True
            if action == 'bets':
                amtcall = 0
                amtraise = float(re.sub('\n', '', actionstring_split[1]))
                print(self.name + " " + action + " " + str(amtraise))
            elif action == 'raises':
                amtcall = maxraise - self.current_potinvestment
                amtraise = float(re.sub('\n', '', actionstring_split[1]))
                print(self.name + " " + action + " " + str(amtraise))
            elif action == 'calls':
                amtcall = maxraise - self.current_potinvestment
                print(self.name + " " + action + " " + str(amtcall))
            else:
                print(self.name + " " + action)

        return [action, amtcall, amtraise]

    def print_something(self, something):
        print(self.name + " " + something)
    
    def print_weights(self):
        print(self.preflop_weights)
        print(self.postflop_weights)

    ################ Genetic Algorithm ########################

    def mutate(self):
        #preflop
        mutate_percentage = 0.05

        ############## Linear Regression ################
        for (i, j), value in np.ndenumerate(self.preflop_weights):
            r = rand.uniform(0, 1)
            if r <= mutate_percentage:
                self.preflop_weights[i, j] += rand.uniform(-4, 4)
        
        ############## Neural Net ################
        
        # for (i, j), value in np.ndenumerate(self.preflop_weights):
        #     r = rand.uniform(0, 1)
        #     if r <= mutate_percentage:
        #         self.preflop_weights[i, j] = rand.uniform(-1, 1)

        # for (i, j), value in np.ndenumerate(self.preflop_weights2):
        #     r = rand.uniform(0, 1)
        #     if r <= mutate_percentage:
        #         self.preflop_weights2[i, j] = rand.uniform(-1, 1)


        #postflop
        mutate_percentage = 0.05

        ############## Linear Regression ################
        for (i, j), value in np.ndenumerate(self.postflop_weights):
            r = rand.uniform(0, 1)
            if r <= mutate_percentage:
                self.postflop_weights[i, j] += rand.uniform(-4, 4)

        ############## Neural Net ################
        
        # for (i, j), value in np.ndenumerate(self.postflop_weights):
        #     r = rand.uniform(0, 1)
        #     if r <= mutate_percentage:
        #         self.postflop_weights[i, j] = rand.uniform(-1, 1)

        # for (i, j), value in np.ndenumerate(self.postflop_weights2):
        #     r = rand.uniform(0, 1)
        #     if r <= mutate_percentage:
        #         self.postflop_weights2[i, j] = rand.uniform(-1, 1)
        
    def breed(self, parent1, parent2):
        #preflop
        preflop_weights_par1 = parent1.get_preflop_weights()
        preflop_weights_par2 = parent2.get_preflop_weights()

        ################### Linear Regression ####################
        parent1_percentage = 0.5
        for (i,j), value in np.ndenumerate(self.preflop_weights):
            r = rand.uniform(0, 1)
            if r <= parent1_percentage:
                self.preflop_weights[i, j] = preflop_weights_par1[0][i, j]
            else:
                self.preflop_weights[i, j] = preflop_weights_par2[0][i, j]

        ################### Neural Network ####################
        # parent1_percentage = 0.5
        # for (i,j), value in np.ndenumerate(self.preflop_weights):
        #     r = rand.uniform(0, 1)
        #     if r <= parent1_percentage:
        #         self.preflop_weights[i, j] = preflop_weights_par1[0][i, j]
        #     else:
        #         self.preflop_weights[i, j] = preflop_weights_par2[0][i, j]
        
        # for (i,j), value in np.ndenumerate(self.preflop_weights2):
        #     r = rand.uniform(0, 1)
        #     if r <= parent1_percentage:
        #         self.preflop_weights2[i, j] = preflop_weights_par1[1][i, j]
        #     else:
        #         self.preflop_weights2[i, j] = preflop_weights_par2[1][i, j]

        #postflop
        postflop_weights_par1 = parent1.get_postflop_weights()
        postflop_weights_par2 = parent2.get_postflop_weights()

        ################### Linear Regression ####################
        parent1_percentage = 0.5
        for (i,j), value in np.ndenumerate(self.postflop_weights):
            r = rand.uniform(0, 1)
            if r <= parent1_percentage:
                self.postflop_weights[i, j] = postflop_weights_par1[0][i, j]
            else:
                self.postflop_weights[i, j] = postflop_weights_par2[0][i, j]

        ################### Neural Network ####################
        # parent1_percentage = 0.5
        # for (i,j), value in np.ndenumerate(self.postflop_weights):
        #     r = rand.uniform(0, 1)
        #     if r <= parent1_percentage:
        #         self.postflop_weights[i, j] = postflop_weights_par1[0][i, j]
        #     else:
        #         self.postflop_weights[i, j] = postflop_weights_par2[0][i, j]
        
        # for (i,j), value in np.ndenumerate(self.postflop_weights2):
        #     r = rand.uniform(0, 1)
        #     if r <= parent1_percentage:
        #         self.postflop_weights2[i, j] = postflop_weights_par1[1][i, j]
        #     else:
        #         self.postflop_weights2[i, j] = postflop_weights_par2[1][i, j]
    


        
