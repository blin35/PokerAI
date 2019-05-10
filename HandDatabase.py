#! /Applications/anaconda3/bin/python

import numpy as np
import pandas as pd

def loaddatabase():
    preflopdb = pd.read_csv('Preflop_db.csv')
    return preflopdb

if __name__ == "__main__":
    startcard = loaddatabase()
    print(startcard)
    pass