#! /Applications/anaconda3/bin/python
from PlayerNeuralNet import Player
from Rulebook import Rulebook
from Deck import Deck

class Table:
    def __init__(self,myname,tablename, smallblind, bigblind, maxseats, rulebook_init, board_init, deck_init):
        self.name = tablename
        self.player1_name = myname
        self.smallblind_amt = smallblind
        self.bigblind_amt = bigblind
        self.button = 1
        self.smallblind = 0
        self.bigblind = 0
        self.maxseats = maxseats
        self.playersdict = {}
        self.seatdict = {}
        self.all_ins = {}
        self.turnorder = []
        self.maxraise = 0.00
        self.currpot = 0.00
        self.rulebook = rulebook_init
        self.board = board_init
        self.deck = deck_init
    
    def reset(self, player_reset_status = 'Inactive'):
        self.board.clear()
        for activeplayer in self.seatdict.values():
            self.playersdict[activeplayer].reset(player_reset_status)
        self.turnorder.clear()
        self.all_ins = {}

    def add_player(self, playername, seat, stack, playertype = 'Computer'):
        if playername in self.playersdict.keys():
            self.playersdict[playername].updatestack(stack)
            self.playersdict[playername].activate()
        else:
            self.playersdict[playername] = Player(playername, seat, stack, self.rulebook, self.board, playertype)
            self.seatdict[seat] = playername
    
    def calc_amountcall(self, currplayer):
        curr_inpot = self.playersdict[currplayer].get_currentpotinvestment()
        amtcall = self.maxraise - curr_inpot
        return amtcall

    def newaction(self, currplayer, curraction, amtcall, amtraise):
        if curraction == 'folds':
            self.playersdict[currplayer].addaction(curraction, self.maxraise)
            self.nextturn(True)
        else:
            self.nextturn(False)
            prev_invest = self.playersdict[currplayer].get_currentpotinvestment()
            self.playersdict[currplayer].addaction(curraction, amtcall + amtraise)
            if curraction == 'raises':
                self.addpot(amtcall + amtraise)
                self.maxraise += amtraise
            if curraction == 'bets':
                self.addpot(amtraise)
                self.maxraise += amtraise
            elif curraction == 'calls':
                self.addpot(amtcall)
            
            self.currpot = round(self.currpot, 2)
            
            ########### Add to Side Pots ###########
            if len(self.all_ins.keys()) > 0:
                for all_in_player in self.all_ins.keys():
                    if self.playersdict[all_in_player].get_currentpotinvestment() > 0.00:
                        self.all_ins[all_in_player] += max(min(self.playersdict[currplayer].get_currentpotinvestment(), 
                        self.playersdict[all_in_player].get_currentpotinvestment()) - prev_invest, 0.00)
            
            ############ New All-in ################
            if round(self.playersdict[currplayer].get_stack(), 2) == 0.00:
                self.playersdict[currplayer].allin()
                sidepot = 0
                for player in self.playersdict.keys():
                    sidepot += min(self.playersdict[player].getpotinvestment(), self.playersdict[currplayer].getpotinvestment())
                self.all_ins[currplayer] = sidepot
    
    def getplayers_in(self):
        return len(self.turnorder)
    
    def remove_player(self, playername):
        seat = 0
        if playername in self.playersdict.keys():
            seat = self.playersdict[playername].getseat()
        if seat > 0:
            del self.playersdict[playername]
            del self.seatdict[seat]
        
    def deactivate_player(self, currplayer):
        self.playersdict[currplayer].deactivate()

    def reset_turnorder_preflop(self, button, printblinds = False):
        self.button = button
        self.turnorder.clear()
        for filled_seat in sorted(self.seatdict.keys()):
            if self.playersdict[self.seatdict[filled_seat]].get_status() != 'Inactive':
                self.turnorder.append(filled_seat)
        numplayers = len(self.turnorder)
        x = 0
        while self.turnorder[x] != button:
            x = x + 1
        x = x + 1
        if x >= numplayers:
            smallblind_index = 0
            bigblind_index = 1
        else:
            smallblind_index = x
            x = x + 1
            if x >= numplayers:
                bigblind_index = 0
            else:
                bigblind_index = x
        self.bigblind = self.turnorder[bigblind_index]
        self.smallblind = self.turnorder[smallblind_index]
        while self.turnorder[0] != self.button:
            self.nextturn(False)

        for i, a in enumerate(self.turnorder):
            self.playersdict[self.seatdict[a]].updateposition(i)
            if a == self.smallblind:
                smallblind_paid = self.playersdict[self.seatdict[a]].makearaise(self.smallblind_amt)
                if printblinds:
                    self.playersdict[self.seatdict[a]].print_something('posts ' + str(smallblind_paid) + ' in blinds')
                if self.playersdict[self.seatdict[a]].get_stack() < 0.01:
                    self.playersdict[self.seatdict[a]].print_something('is All-In')
            elif a == self.bigblind:
                bigblind_paid = self.playersdict[self.seatdict[a]].makearaise(self.bigblind_amt) 
                if printblinds:
                    self.playersdict[self.seatdict[a]].print_something('posts ' + str(bigblind_paid) + ' in blinds')
                if self.playersdict[self.seatdict[a]].get_stack() < 0.01:
                    self.playersdict[self.seatdict[a]].print_something('is All-In')
        while self.turnorder[numplayers - 1] != self.bigblind:
            self.nextturn(False)
        
        self.maxraise = self.bigblind_amt
        self.currpot = smallblind_paid + bigblind_paid

    def reset_turnorder_postflop(self):
        for player in self.playersdict.keys():
            self.playersdict[player].new_street()
        first_to_act = self.smallblind
        while True:
            if first_to_act in self.turnorder:
                break
            else:
                first_to_act = first_to_act + 1
                if first_to_act > 6:
                    first_to_act = 1
        while self.turnorder[0] != first_to_act:
            self.nextturn(False)
        
        self.maxraise = 0.00
        
    def whose_turn(self):
        return self.turnorder[0]

    def hand_dealt(self, card1, card2):
        self.playersdict[self.player1_name].new_hand(card1, card2)

    def addpot(self, moneyin):
        self.currpot += moneyin
    
    def nextturn(self,folded):
        if folded:
            self.turnorder.pop(0)
        else:
            self.turnorder.append(self.turnorder.pop(0))
    
    def create_db_column(self, actionvalue, street, hand_id, row_id):
        return self.playersdict[self.player1_name].get_regression_params(actionvalue, self.maxraise, len(self.turnorder), street, self.bigblind_amt, hand_id, row_id)
    
    def add_cards(self, cards):
        self.board = self.rulebook.add_cards(cards, self.board)

    def add_winner(self, winner, winnings = 0):
        if winnings == 0:
            winnings = self.currpot()
        self.playersdict[winner].add_win(winnings)
    
    def splitpot(self):
        amount_each = round(self.currpot/2, len(self.turnorder))
        for activeseat in self.turnorder:
            self.playersdict[self.seatdict[activeseat]].add_win(amount_each)
    
    def get_winnings(self, player):
        return self.playersdict[player].getpotinvestment() * -1
    
    ############################ Simulation Functions ##################################
    
    def players_left(self):
        return len(self.playersdict.keys())
    
    def get_max_age(self):
        curr_max_age = 0
        curr_oldest_player = 'Player1'
        for player in self.playersdict.keys():
            currage = self.playersdict[player].get_age()
            if currage > curr_max_age:
                curr_oldest_player = player
                curr_max_age = currage
        
        return (curr_oldest_player, curr_max_age)

    
    def true_turnorder_length(self):
        length = 0
        for seat in self.turnorder:
            if self.playersdict[self.seatdict[seat]].get_status() == 'Active':
                length += 1
        return length

    def dealcards(self, printhands = True):
        self.deck.reset()
        while True:
            self.button += 1
            if self.button == 7:
                self.button = 1
            if self.button in self.seatdict.keys():
                break
        
        self.reset_turnorder_preflop(self.button, True)

        for player in self.playersdict.keys():
            newhand = self.deck.deal(2)
            self.playersdict[player].new_hand(newhand[0], newhand[1], printhands)
        
    def runpreflop(self):
        currmaxraiser = self.bigblind
        currmaxraise = self.maxraise
        while True:
            if len(self.turnorder) == 1:
                break
            elif self.true_turnorder_length() <= 1:
                currplayer = self.seatdict[self.turnorder[0]]
                if self.playersdict[currplayer].get_currentpotinvestment() < self.maxraise and self.playersdict[currplayer].get_status() != 'All-In':
                    newaction = self.playersdict[currplayer].new_action(self.maxraise, len(self.turnorder), 'Preflop', self.bigblind_amt)
                    if newaction[0] == 'raises':
                        newaction[0] = 'calls'
                        newaction[2] = 0.00
                        self.playersdict[currplayer].print_something('can only call ' + str(newaction[1]))
                    self.newaction(currplayer,newaction[0], newaction[1], newaction[2])
                else:
                    break
            elif self.turnorder[0] == currmaxraiser:
                if currmaxraise == self.bigblind_amt:
                    currplayer = self.seatdict[self.turnorder[0]]
                    if self.playersdict[currplayer].get_status() != 'All-In':
                        newaction = self.playersdict[currplayer].new_action(self.maxraise, len(self.turnorder), 'Preflop', self.bigblind_amt)
                        self.newaction(currplayer,newaction[0], newaction[1], newaction[2])
                    else:
                        self.nextturn(False)   

                    if currmaxraise == self.bigblind_amt:
                        break
                    else:
                        currmaxraise = self.maxraise
            
                else:
                    break
            else:
                currplayer = self.seatdict[self.turnorder[0]]
                if self.playersdict[currplayer].get_status() != 'All-In':
                    newaction = self.playersdict[currplayer].new_action(self.maxraise, len(self.turnorder), 'Preflop', self.bigblind_amt)
                    self.newaction(currplayer,newaction[0], newaction[1], newaction[2])
                else:
                    self.nextturn(False)   

                if self.maxraise > currmaxraise:
                    currmaxraise = self.maxraise
                    currmaxraiser = self.playersdict[currplayer].getseat()
        
        if len(self.turnorder) == 1:
            currplayer = self.seatdict[self.turnorder[0]]
            self.distribute_winnings([[currplayer, 0]])

        return len(self.turnorder)


    def runpostflop(self, numcards, street):
        self.reset_turnorder_postflop()

        newcards = self.deck.deal(numcards)
        for card in newcards:
            print(card.get_value() + card.get_suit())
        self.add_cards(newcards)
        currmaxraiser = self.turnorder[0]
        currmaxraise = self.maxraise
        firstturn = True
        while True:
            if len(self.turnorder) == 1:
                break
            elif self.true_turnorder_length() <= 1:
                currplayer = self.seatdict[self.turnorder[0]]
                if self.playersdict[currplayer].get_currentpotinvestment() < self.maxraise and self.playersdict[currplayer].get_status() != 'All-In':
                    newaction = self.playersdict[currplayer].new_action(self.maxraise, len(self.turnorder), street, self.bigblind_amt)
                    if newaction[0] == 'raises':
                        newaction[0] = 'calls'
                        newaction[2] = 0.00
                        self.playersdict[currplayer].print_something('can only call ' + str(newaction[1]))
                    self.newaction(currplayer,newaction[0], newaction[1], newaction[2])
                else:
                    break
            elif self.turnorder[0] == currmaxraiser:
                if firstturn:
                    currplayer = self.seatdict[self.turnorder[0]]
                    if self.playersdict[currplayer].get_status() != 'All-In':
                        newaction = self.playersdict[currplayer].new_action(self.maxraise, len(self.turnorder), street, self.bigblind_amt)
                        self.newaction(currplayer,newaction[0], newaction[1], newaction[2])
                    else:
                        self.nextturn(False)                    
                    if self.maxraise > currmaxraise:
                        currmaxraise = self.maxraise
                    
                    firstturn = False

                else:
                    break
            else:
                currplayer = self.seatdict[self.turnorder[0]]
                if self.playersdict[currplayer].get_status() != 'All-In':
                    newaction = self.playersdict[currplayer].new_action(self.maxraise, len(self.turnorder), street, self.bigblind_amt)
                    self.newaction(currplayer,newaction[0], newaction[1], newaction[2])
                else:
                    self.nextturn(False)   
                
                if self.maxraise > currmaxraise:
                    currmaxraise = self.maxraise
                    currmaxraiser = self.playersdict[currplayer].getseat()

        #################### Distribute winnings #########################
        if len(self.turnorder) == 1:
            currplayer = self.seatdict[self.turnorder[0]]
            self.distribute_winnings([[currplayer, 0]])
        elif street == 'River':
            winners = []
            for seat in self.turnorder:
                currplayer = self.seatdict[seat]
                currhand = self.rulebook.calc_hand(self.playersdict[currplayer].get_hand(), self.board)
                currhandvalue = currhand[0]
                self.playersdict[self.seatdict[seat]].print_something(currhand[2])
                j = 0
                while j < len(winners):
                    if winners[j][1] < currhandvalue:
                        winners.insert(j, [currplayer, currhandvalue])
                        j += 1
                        break
                    j+=1    
                if j == len(winners):
                    winners.append([currplayer, currhandvalue])

            self.distribute_winnings(winners)
        return len(self.turnorder)

    def distribute_winnings(self, winners):
        if len(winners) == 1:
            self.playersdict[winners[0][0]].add_win_sim(self.currpot)
            self.currpot = 0.00
        elif len(winners) > 1:
            currwinners = []
            while round(self.currpot, 2) > 0.00:
                maxhandvalue = winners[0][1]
                while len(winners) >= 1:
                    if winners[0][1] < maxhandvalue:
                        break
                    else:
                        currwinners.append(winners.pop(0))

                if len(currwinners) == 1:
                    if currwinners[0][0] in self.all_ins.keys():
                        self.playersdict[currwinners[0][0]].add_win_sim(self.all_ins[currwinners[0][0]])
                        self.currpot -= self.all_ins[currwinners[0][0]]
                    else:
                        self.playersdict[currwinners[0][0]].add_win_sim(self.currpot)
                        self.currpot = 0.00
                elif len(currwinners) > 1:
                    minwinner = ''
                    minsidepot = self.currpot
                    if len(self.all_ins.keys()) >= 1:
                        for finalwinner in currwinners:
                            if finalwinner[0] in self.all_ins.keys():
                                if self.all_ins[finalwinner[0]] < minsidepot:
                                    minsidepot = self.all_ins[finalwinner[0]]
                                    minwinner = finalwinner
                    for finalwinner in currwinners:
                        self.playersdict[finalwinner[0]].add_win_sim(round(minsidepot/len(currwinners), 2))
                        if minwinner != '' and finalwinner[0] != minwinner:
                            winners.insert(0, finalwinner)
                    self.currpot -= minsidepot * len(currwinners)

        activeplayers = list(self.playersdict.keys())
        for j in range(0, len(activeplayers)):
            if len(self.playersdict.keys()) <= 2:
                break
            elif self.playersdict[activeplayers[j]].get_stack() < 0.01:
                self.remove_player(activeplayers[j])
    
    def print_weights(self):
        for player in self.playersdict.keys():
            self.playersdict[player].print_weights()

    def return_top2_players(self):
        maxstack = -1
        maxstackplayer = ''
        maxstack2 = -1
        maxstackplayer2 = ''
        for player in self.playersdict.keys():
            currstack = self.playersdict[player].get_stack()
            if currstack > maxstack:
                maxstack2 = maxstack
                maxstackplayer2 = maxstackplayer 
                maxstack = currstack
                maxstackplayer = player
            elif currstack > maxstack2:
                maxstack2 = currstack
                maxstackplayer2 = player
                
        
        players_to_keep = (maxstackplayer, maxstackplayer2)
        for player in list(self.playersdict.keys()):
            if player not in players_to_keep:
                self.remove_player(player)
            else:
                self.playersdict[player].add_age()
        print(maxstackplayer + ', ' + maxstackplayer2)
        return players_to_keep
    
    def get_postflop_weights(self, player):
        return self.playersdict[player].get_postflop_weights()
    
    def get_preflop_weights(self, player):
        return self.playersdict[player].get_preflop_weights()

    def get_stack(self, player):
        return self.playersdict[player].get_stack()
    
    def adjustweights(self, weights1, weights2):
        parent1 = Player('Parent1', 0, 0, self.rulebook, self.board, 'Computer', randomweights = False, preflopweights = weights1[0], postflopweights = weights1[1])
        parent2 = Player('Parent2', 0, 0, self.rulebook, self.board, 'Computer', randomweights = False, preflopweights = weights2[0], postflopweights = weights2[1])
        for player in self.playersdict.keys():
            if self.playersdict[player].getseat() < 6:
                self.playersdict[player].breed(parent1, parent2)
        
    
    def breednewplayers(self):
        if len(self.playersdict.keys()) == 2:
            i = 1
            parents = []
            for player in self.playersdict.keys():
                self.playersdict[player].updateseat(i)
                self.playersdict[player].updatename('Player'+str(i))
                i += 1
                self.playersdict[player].updatestack(2.00)
                parents.append(self.playersdict[player])

            self.playersdict = {}
            self.seatdict = {}
            self.playersdict['Player1'] = parents[0]
            self.playersdict['Player2'] = parents[1]
            self.seatdict[1] = 'Player1'
            self.seatdict[2] = 'Player2'

            ##### breed 3 other players ######

            for i in range(3, 5):
                self.add_player('Player' + str(i), i, 2.00, 'Computer')
                self.playersdict['Player' + str(i)].breed(parents[0], parents[1])
                self.playersdict['Player' + str(i)].mutate()
            
            ##### player 5,6 random ######
            self.add_player('Player5', 5, 2.00, 'Computer')
            self.add_player('Player6', 6, 2.00, 'Computer')
            

                
            
        




    
