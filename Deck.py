#! /Applications/anaconda3/bin/python
from Card import Card
import random

class Deck:
    def __init__(self):
        self.valuelist = ['2','3','4','5','6','7','8','9','T','J','Q','K','A']
        self.suitlist = ['d', 'c', 'h', 's']
        self.cards = [Card(i+j) for i in self.valuelist for j in self.suitlist]
    
    def shuffle(self):
        for i in range(len(self.cards) - 1, 0, -1):
            r = random.randint(0, i - 1)
            self.cards[i], self.cards[r] = self.cards[r], self.cards[i]

    def deal(self, numcards):
        cardsdealt = []
        i = 1
        while i <= numcards:
            cardsdealt.append(self.cards.pop(0))
            i += 1
        
        return cardsdealt
    
    def reset(self):
        self.cards = [Card(i+j) for i in self.valuelist for j in self.suitlist]
        self.shuffle()     

 