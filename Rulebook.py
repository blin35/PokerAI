#! /Applications/anaconda3/bin/python
from Card import Card

class Rulebook:
    def __init__(self):
        self.valuelist = ['2','3','4','5','6','7','8','9','T','J','Q','K','A']
        self.suitlist = ['d', 'c', 'h', 's']
        self.handorder = ["high-card", "pair", "two-pair", "trips", "straight", "flush", "full-house", "quads", "straight-flush"]

    def add_cards(self, cards, allcards):
        for card in cards:
            i = 0
            while (i < len(allcards)):
                if self.valuelist.index(card.get_value()) < self.valuelist.index(allcards[i].get_value()):
                    allcards.insert(i, card)
                    break
                i += 1
            
            if i == len(allcards):
                allcards.append(card)
        
        return allcards
    
    def add_pairstripsquads(self, currpairstripsquads, pairstripsquads):
        j = 0
        while j < len(pairstripsquads):
            if (len(currpairstripsquads) > len(pairstripsquads[j]) or 
                (len(currpairstripsquads) == len(pairstripsquads[j]) and 
                self.valuelist.index(currpairstripsquads[0].get_value()) > self.valuelist.index(pairstripsquads[j][0].get_value()))):
                pairstripsquads.insert(j, currpairstripsquads)
                break
            else:
                j += 1
                
        if j == len(pairstripsquads):
            pairstripsquads.append(currpairstripsquads)
        return pairstripsquads
    
    def calc_hand(self, hand, board):
        valuematrix = [0,0,0,0,0,0]
        allcards = []
        
        self.add_cards(hand, allcards)
        self.add_cards(board, allcards)

        straight_flush = False
        straight = False
        flush = False
        fullhouse = False
        suit_count = [[],[],[],[]]
        connected = []
        currconnected = [allcards[0]]
        pairstripsquads = []
        currpairstripsquads = [allcards[0]]
        suit_count[self.suitlist.index(allcards[0].get_suit())].append(allcards[0])
        for i in range(1, len(allcards)):
            #pairs:
            if self.value_distance(allcards[i-1], allcards[i]) == 0:
                currpairstripsquads.append(allcards[i])
            else:
                pairstripsquads = self.add_pairstripsquads(currpairstripsquads, pairstripsquads)
                currpairstripsquads = [allcards[i]]
            # straight:
                if abs(self.value_distance(allcards[i-1], allcards[i])) == 1:
                    currconnected.append(allcards[i])
                else:
                    connected.append(currconnected)
                    currconnected = [allcards[i]]
            # last card:
            if i == len(allcards) - 1:
                pairstripsquads = self.add_pairstripsquads(currpairstripsquads, pairstripsquads)
                connected.append(currconnected)
            #flush:
            suit_count[self.suitlist.index(allcards[i].get_suit())].append(allcards[i])

        #straight
        lengths_connected = list(map(lambda x: len(x), connected))
        max_connected = max(lengths_connected)
        if max_connected >= 5:
            straight = True
            straightconnected = connected[lengths_connected.index(max_connected)]
            previous_suit = straightconnected[0].get_suit()
            cardnumber = 1
            while cardnumber < len(straightconnected):
                card = straightconnected[cardnumber]
                if card.get_suit() != previous_suit:
                    if cardnumber == 1 and max_connected > 5:
                        previous_suit = card.get_suit()
                        cardnumber += 1
                    else:
                        break
                else:
                    cardnumber += 1
            if cardnumber >= 5:
                straight_flush = True
                straight_flush_high = self.valuelist.index(straightconnected[cardnumber - 1].get_value())
            straight_high = 1 + self.valuelist.index(connected[lengths_connected.index(max_connected)][-1].get_value())
        
        #flush
        lengths_suit = list(map(lambda x: len(x), suit_count))
        max_samesuit = max(lengths_suit)
        if max_samesuit >= 5:
            flush = True
            flush_index = lengths_suit.index(max_samesuit)

        max_samevalue = len(pairstripsquads[0])
        
        #full-house
        if max_samevalue == 3 and len(pairstripsquads) > 1:
            if len(pairstripsquads[1]) > 1:
                fullhouse = True


        #current hand
        #Straight Flush
        hand_value_desc = ''

        if (straight_flush):
            valuematrix[0] = self.handorder.index("straight-flush")
            valuematrix[1] = straight_flush_high
            hand_value_desc = str(self.valuelist[valuematrix[1] - 1]) + ' High'
        #Quads
        elif max_samevalue == 4:
            valuematrix[0] = self.handorder.index("quads")
            valuematrix[1] = 1 + self.valuelist.index(pairstripsquads[0][0].get_value())
            if len(allcards) >= 5:
                valuematrix[2] = 1 + self.valuelist.index(allcards[-1].get_value())
                if valuematrix[1] == valuematrix[2]:
                    valuematrix[2] = 1 + self.valuelist.index(allcards[-5].get_value())
            hand_value_desc = str(self.valuelist[valuematrix[1] - 1])
        #Full House or Trips
        elif fullhouse:
            valuematrix[0] = self.handorder.index("full-house")
            valuematrix[1] = 1 + self.valuelist.index(pairstripsquads[0][0].get_value())
            valuematrix[2] = 1 + self.valuelist.index(pairstripsquads[1][0].get_value())
            hand_value_desc = str(self.valuelist[valuematrix[1] - 1])
        #Flush
        elif flush:
            valuematrix[0] = self.handorder.index("flush")
            for i in range(0,5):
                valuematrix[i + 1] = self.valuelist.index(suit_count[flush_index][(i+1)*-1].get_value())
            hand_value_desc = self.suitlist[flush_index] + ' ' + str(self.valuelist[valuematrix[1] - 1]) + ' High'
        #Straight
        elif straight:
            valuematrix[0] = self.handorder.index("straight")
            valuematrix[1] = straight_high
            hand_value_desc = str(self.valuelist[valuematrix[1] - 1]) + ' High'
        #Trips
        elif max_samevalue == 3:
            valuematrix[0] = self.handorder.index("trips")
            valuematrix[1] = 1 + self.valuelist.index(pairstripsquads[0][0].get_value())
            if len(allcards) >= 4:
                valuematrix[2] = 1 + self.valuelist.index(pairstripsquads[1][0].get_value())
            if len(allcards) >= 5:
                valuematrix[3] = 1 + self.valuelist.index(pairstripsquads[2][0].get_value())
            hand_value_desc = str(self.valuelist[valuematrix[1] - 1])
        #Two pair
        elif max_samevalue == 2 and len(pairstripsquads[1]) == 2:
            valuematrix[0] = self.handorder.index("two-pair")
            valuematrix[1] = 1 + self.valuelist.index(pairstripsquads[0][0].get_value())
            valuematrix[2] = 1 + self.valuelist.index(pairstripsquads[1][0].get_value())
            if len(allcards) >= 5:
                valuematrix[3] = 1 + self.valuelist.index(pairstripsquads[2][0].get_value())
            hand_value_desc = str(self.valuelist[valuematrix[1] - 1]) + '-' + str(self.valuelist[valuematrix[2] - 1])
           #Pair
        elif max_samevalue == 2:
            valuematrix[0] = self.handorder.index("pair")
            valuematrix[1] = 1 + self.valuelist.index(pairstripsquads[0][0].get_value())
            valuematrix[2] = 1 + self.valuelist.index(pairstripsquads[1][0].get_value())
            if len(allcards) >= 4:
                valuematrix[3] = 1 + self.valuelist.index(pairstripsquads[2][0].get_value())
            if len(allcards) >= 5:
                valuematrix[4] = 1 + self.valuelist.index(pairstripsquads[3][0].get_value())
            hand_value_desc = str(self.valuelist[valuematrix[1] - 1])
         #High Card
        else:
            for i in range(0, min(len(pairstripsquads), 5)):
                valuematrix[i + 1] = 1 + self.valuelist.index(pairstripsquads[i][0].get_value())
            hand_value_desc = str(self.valuelist[valuematrix[1] - 1])
        
        valuematrix_weights = [14**5,14**4,14**3,14**2,14**1,1]
        handvalue = sum(x * y for x, y in zip(valuematrix, valuematrix_weights))
        ########################### Outs ###############################
        allouts = 0
        #flush outs
        if max_samesuit == 4:
            allouts += 9
            
        #straight outs
        for i in range(0,len(connected) - 1):
            if len(connected[i]) == 4:
                if allouts == 0:
                    allouts += 8
                else:
                    allouts += 6
            if (len(connected[i]) + len(connected[i + 1]) >= 4):
                if abs(self.value_distance(connected[i][len(connected[i])-1], connected[i + 1][0])) == 1:
                    if allouts == 0:
                        allouts += 4
                    else:
                        allouts += 3
        
        if len(connected[len(connected) - 1]) == 4:
                if allouts == 0:
                    allouts += 4
                else:
                    allouts += 3
        
        return (handvalue, allouts, self.handorder[valuematrix[0]] + ' ' + hand_value_desc)
        

    def gethighcard(self, allcards):
        custom = lambda x: self.valuelist.index(x.get_value())
        return max(map(custom, allcards))
    
    def getkicker(self, allcards):
        custom = lambda x: self.valuelist.index(x.get_value())
        return min(map(custom, allcards))

    def value_distance(self, card1, card2):
        if card1.get_value() == 'A':
            return min(self.valuelist.index('A') - self.valuelist.index(card2.get_value()),
             self.valuelist.index(card2.get_value()) + 1)
        elif card2.get_value() == 'A':
            return (min(self.valuelist.index('A') - self.valuelist.index(card1.get_value()),
             self.valuelist.index(card1.get_value()) + 1)) * -1
        else:
            return self.valuelist.index(card1.get_value()) - self.valuelist.index(card2.get_value())
 