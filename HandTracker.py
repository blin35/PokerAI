#! /Applications/anaconda3/bin/python

import pyautogui, sys


if __name__ == "__main__":
    print('Press Ctrl-C to quit.')
    try:
        while True:
            x, y = pyautogui.position()
            positionStr = 'X: ' + str(x).rjust(4) + ' Y: ' + str(y).rjust(4)
            print(positionStr)
            print('\b' * (len(positionStr) + 2))
            sys.stdout.flush()
    except KeyboardInterrupt:
        print('\n')
    pass