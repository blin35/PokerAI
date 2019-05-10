#! /Applications/anaconda3/bin/python

import pyautogui
import numpy as np
import imutils
import cv2

if __name__ == "__main__":

    playercascade = cv2.CascadeClassifier('ObjectCascades/cascade.xml')
    
    img = pyautogui.screenshot()
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    print(img)
    players = playercascade.detectMultiScale(img, scaleFactor = 1.05, minNeighbors = 5)

    for x,y,w,h in players:
        img = cv2.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 3)
    
    resized = cv2.resize(img, (int(img.shape[1]), int(img.shape[0])))

    cv2.imshow("Gray", resized)
    cv2.waitKey(0)

    cv2.destroyAllWindows()

    pass