#! /Applications/anaconda3/bin/python
from Card import Card
from Rulebook import Rulebook
import random
import numpy

class Player:
    def __init__(self, name, seat, stack, rulebook, board):
        self.status = 'Active'
        self.call_status = 'Uncalled'
        self.name = name
        self.seat = seat
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
        self.preflop_weights = []
        for _ in range(8):
            self.preflop_weights.append(random.uniform(-4, 4))
        self.postflop_weights = []
        for _ in range(7):
            self.postflop_weights.append(random.uniform(-4, 4))
        self.handsplayed = 1
        self.handswon = 0
        self.rulebook = rulebook
    
    def getstack(self):
        return self.stack
    
    def get_hand(self):
        return self.current_hand
    
    def getstatus(self):
        return self.status
    
    def deactivate(self):
        self.status = 'Inactive'
    
    def activate(self):
        self.status = 'Active'
    
    def getseat(self):
        return self.seat
    
    def getpotinvestment(self):
        return self.total_potinvestment + self.current_potinvestment

    def updatestack(self,currstack):
        self.stack = currstack

    def updateposition(self,currposition):
        self.position = currposition
    
    def reset(self):
        self.status = 'Active'
        self.position = 0
        self.total_potinvestment = 0
        self.current_potinvestment = 0
        self.allactions[self.handsplayed] = self.currentactions
        self.currentactions = []
        self.handsplayed += 1
        self.current_hand = []

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
        if self.stack >= amount:
            self.current_potinvestment += amount
            self.stack -= amount
            self.current_potinvestment = round(self.current_potinvestment, 2)
        else:
            self.current_potinvestment = self.stack
            self.stack = 0

    def add_win(self, winnings):
        self.handswon += 1
        self.total_potinvestment -= winnings
    
    def new_street(self):
        self.total_potinvestment += self.current_potinvestment
        self.current_potinvestment = 0
    
    def new_hand(self, card1, card2):
        self.current_hand.append(card1)
        self.current_hand.append(card2)
        print(self.name + " " + str(self.stack))
        print(card1.get_value() + card1.get_suit() + " " + card2.get_value() + card2.get_suit())
    
    def get_regression_params(self, actionvalue, maxraise, playersin, street, blind, hand_id, row_id):
        if street == "preflop":
            pocket = False
            suited = False
            if self.current_hand[0].get_value() == self.current_hand[1].get_value():
                pocket = True
            if self.current_hand[0].get_suit() == self.current_hand[1].get_suit():
                suited = True
            return  (row_id, actionvalue/blind, self.rulebook.gethighcard(), self.rulebook.getkicker(),
                playersin, pocket, suited, round((self.total_potinvestment + self.current_potinvestment)/blind, 1), round((maxraise - self.current_potinvestment)/blind, 1), hand_id)
        elif street == "flop" or street == "turn":
            self.rulebook.calc_hand()
            return  (row_id, actionvalue/blind, self.rulebook.get_handvalue(), self.rulebook.get_outs(),
                round((self.total_potinvestment + self.current_potinvestment)/blind, 1), round((maxraise - self.current_potinvestment)/blind, 1), playersin, round(self.stack/blind, 2), hand_id)
        else:
            self.rulebook.calc_hand()
            return  (row_id, actionvalue/blind, self.rulebook.get_handvalue(),
                round((self.total_potinvestment + self.current_potinvestment)/blind, 1), (maxraise - self.current_potinvestment)/blind, playersin, round(self.stack/blind, 2), hand_id)
        

    ################ Simulation ########################
    def add_win_sim(self, winnings):
        print(self.name + " Won " + str(winnings))
        self.handswon += 1
        self.total_potinvestment -= winnings
        self.stack += winnings
    
    def new_action(self, maxraise, playersin, street, blind):
        if street == "Preflop":
            pocket = False
            suited = False
            if self.current_hand[0].get_value() == self.current_hand[1].get_value():
                pocket = True
            if self.current_hand[0].get_suit() == self.current_hand[1].get_suit():
                suited = True
            xvals = (self.rulebook.gethighcard(self.current_hand), self.rulebook.getkicker(self.current_hand),
                playersin, pocket, suited, round((self.total_potinvestment + self.current_potinvestment)/blind, 1), round((maxraise - self.current_potinvestment)/blind, 1))
            decisionvalue = sum(x*y for x,y in list(zip(self.preflop_weights, xvals)))
        else:
            streets = ['Flop', 'Turn', 'River']
            handvalue = self.rulebook.calc_hand(self.current_hand, self.board)
            boardvalue = self.rulebook.calc_hand([], self.board)[0]
            truehandvalue = (handvalue[0] - boardvalue)/14**5
            xvals = (truehandvalue, handvalue[1],
                round((self.total_potinvestment + self.current_potinvestment)/blind, 1), round((maxraise - self.current_potinvestment)/blind, 1), playersin, round(self.stack/blind, 2), streets.index(street))
            decisionvalue = sum(x*y for x,y in list(zip(self.postflop_weights, xvals)))

        action = ''
        amtcall = 0.00
        amtraise = 0.00
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
                amtraise = random.randint(2, 4)/100
                print(self.name + " " + action + " " + str(amtraise))
            else:
                action = 'calls'
                amtcall = maxraise - self.current_potinvestment
                print(self.name + " " + action + " " + str(amtcall))
                if amtcall == 0.00:
                    action = 'checks'
                    print(self.name + " " + action)
        else:
            if maxraise == 0.00:
                action = 'bets'
                amtcall = 0.00
                amtraise = random.randint(2, 4)/100
                print(self.name + " " + action + " " + str(amtraise))
            else:
                action = 'raises'
                amtcall = maxraise - self.current_potinvestment
                amtraise = min(self.stack, (maxraise - self.current_potinvestment))
                print(self.name + " " + action + " " + str(amtraise))

        amtcall = round(amtcall, 2)
        amtraise = round(amtraise, 2)
        return (action, amtcall, amtraise)

    def print_something(self, something):
        print(self.name + " " + something)
    
    def print_weights(self):
        print(self.preflop_weights)
        print(self.postflop_weights)
        
