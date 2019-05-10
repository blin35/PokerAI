#! /Applications/anaconda3/bin/python

import pandas as pd
import re
import sys
import statsmodels.formula.api as sm

sys.tracebacklimit = 0

def load_preflop_database():
    preflopdb = pd.read_csv('Preflop_db.csv')
    return preflopdb

def load_postflop_database():
    postflopdb = pd.read_csv('Postflop_db.csv')
    return postflopdb

def load_id_links():
    IDdb = pd.read_csv('ID_db.csv')
    return IDdb

if __name__ == "__main__":

    
    #Preflop DB
    preflopdb = load_preflop_database()

    #Postflop DB
    postflopdb = load_postflop_database()

    #ID DB
    IDdb = load_id_links()

    #lasthandid = 0
    #lastflopid = 0

    #preflop                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
    preflop_result = sm.ols(formula = 'Decision ~ High_card + Kicker + NumIn + Pocket + Suited + PotInvestment + AmountToCall',
    data = preflopdb).fit()
    print(preflop_result.params)
    print(preflop_result.summary())

    #postflop
    postflop_result = sm.ols(formula = 'Decision ~ Hand + Street + Outs + PotInvestment + AmountToCall + NumCalls + Bankroll',
    data = postflopdb).fit()
    print(postflop_result.params)
    print(postflop_result.summary())
    pass