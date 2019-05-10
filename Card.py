#! /Applications/anaconda3/bin/python

class Card:
    def __init__(self, value_suit):
        self.value = value_suit[0]
        self.suit = value_suit[1]

    def get_value(self):
        return self.value
    
    def get_suit(self):
        return self.suit