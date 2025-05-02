# -*- coding: utf-8 -*-
"""
Created on Fri Oct 11 15:15:33 2024

#https://github.com/maximus009/VideoPlayer/blob/master/new_test_3.py


@author: klab
"""
import cv2, numpy as np
import sys
from time import sleep
import warnings
warnings.filterwarnings("ignore")





# video = 'J:/RAW_DATA/PHOTOMETRY/RECORDINGS/08132024_LS/nLight1A/Video2024-08-13T14_14_14.avi'
# tsFile = 'J:/RAW_DATA/PHOTOMETRY/RECORDINGS/08132024_LS/nLight1A/VideoTime2024-08-13T14_14_14.csv'
# photometryTimeFile = 'J:/RAW_DATA/PHOTOMETRY/RECORDINGS/08132024_LS/nLight1A/DataTime2024-08-13T14_14_14.csv'


video = 'J:/RAW_DATA/PHOTOMETRY/RECORDINGS/08222024_LS/nLight1C/Video2024-08-22T17_15_02.avi'
tsFile = 'J:/RAW_DATA/PHOTOMETRY/RECORDINGS/08222024_LS/nLight1C/VideoTime2024-08-22T17_15_02.csv'
photometryTimeFile = 'J:/RAW_DATA/PHOTOMETRY/RECORDINGS/08222024_LS/nLight1C/DataTime2024-08-22T17_15_02.csv'






def flick(x):
    pass

def process(im):
    return cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

def timeSlide(idx, MasterTrackBar, SlaveTrackbar):
    print('TODO')

cv2.namedWindow('image')
cv2.moveWindow('image',250,150)
cv2.namedWindow('controls')
cv2.moveWindow('controls',250,50)

controls = np.zeros((50,750),np.uint8)
cv2.putText(controls, "W: Play, S: Stay, A: Prev, D: Next, E: Fast, Q: Slow, Esc: Exit", (40,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 255)

displayFrameRate = 60

print('------------------------')
print('Video File: ', video.split('/')[-1])
print('Timestamps File: ', tsFile.split('/')[-1])

#Video
cap = cv2.VideoCapture(video)
tots = cap.get(cv2.CAP_PROP_FRAME_COUNT)

#Video timestamps
timeStamps = np.genfromtxt(tsFile, delimiter=',')
resetTimeStamps = [x-timeStamps[0] for x in timeStamps]
periods = np.array(resetTimeStamps[1:]) - np.array(resetTimeStamps[:-1])
frameRates = 1./periods
print ('Frame Rate +/-SD: {:.2f} +/- {:.2f}'.format(np.nanmean(frameRates), np.nanstd(frameRates)))
print('{} frames in file'.format(int(tots)))
print('Total duration: {:.2f}s'.format(resetTimeStamps[-1]))

#Photometry timestamps
dataStamps = np.genfromtxt(photometryTimeFile, delimiter=',')[:,1]
resetDataStamps = [(x-dataStamps[0])/1000 for x in dataStamps]

tsLag = dataStamps[0]/1000 - timeStamps[0]
if tsLag < 0: 
    print('Video lags {:.2f}s behind photometry data'.format(tsLag))
else: 
    print('Video is {:.2f}s ahead of photometry data'.format(tsLag))
    tsLag = tsLag*-1


#Initiate timer bars for controls 
timeBar = cv2.createTrackbar('Time', 'image', 0, int(resetTimeStamps[-1])+10, flick) #Adding 10 seconds in case of lag w/ photometry data
cv2.setTrackbarPos('Time', 'image', 0)

frameBar = cv2.createTrackbar('Frame','image', 0,int(tots)-1, flick)
cv2.setTrackbarPos('Frame','image',0)

rateBar = cv2.createTrackbar('Rate','image', 0, 100, flick)
cv2.setTrackbarPos('Rate','image',30)



status = 'stay'

i = 0

while True:
  cv2.imshow("controls",controls)
  try:
    if i==tots-1:
      i=0
    cap.set(cv2.CAP_PROP_POS_FRAMES, i)
    ret, im = cap.read()
    r = 750.0 / im.shape[1]
    dim = (750, int(im.shape[0] * r))
    im = cv2.resize(im, dim, interpolation = cv2.INTER_AREA)
    if im.shape[0]>600:
        im = cv2.resize(im, (500,500))
        controls = cv2.resize(controls, (im.shape[1],25))
    #cv2.putText(im, status, )
    cv2.imshow('image', im)
    status = { ord('s'):'stay', ord('S'):'stay',
                ord('w'):'play', ord('W'):'play',
                ord('a'):'prev_frame', ord('A'):'prev_frame',
                ord('d'):'next_frame', ord('D'):'next_frame',
                ord('q'):'slow', ord('Q'):'slow',
                ord('e'):'fast', ord('E'):'fast',
                ord('c'):'snap', ord('C'):'snap',
                -1: status, 
                27: 'exit'}[cv2.waitKey(10)]

    if status == 'play':
      #frame_rate = cv2.getTrackbarPos('F','image')
      frame_rate = int(frameRates[i])

      #sleep((0.1-frame_rate/1000.0)**21021)
      #print(1./frame_rate)
      #sleep(1./frame_rate/1.5)
      sleep(1./displayFrameRate)

      i+=1
      cv2.setTrackbarPos('Frame','image',i)
      cv2.setTrackbarPos('Time', 'image', int(resetTimeStamps[i])-int(tsLag))
      cv2.setTrackbarPos('Rate', 'image', int(frameRates[i]))
      continue
  
    if status == 'stay':
      i = cv2.getTrackbarPos('Frame','image')
      cv2.setTrackbarPos('Frame','image',i)
      cv2.setTrackbarPos('Time', 'image', int(resetTimeStamps[i])-int(tsLag))
      cv2.setTrackbarPos('Rate', 'image', int(frameRates[i]))
      
    if status == 'exit':
        cv2.destroyAllWindows()
        break
    
    if status=='prev_frame':
        i-=1
        cv2.setTrackbarPos('Frame','image',i)
        cv2.setTrackbarPos('Time', 'image', int(resetTimeStamps[i])-int(tsLag))
        cv2.setTrackbarPos('Rate', 'image', int(frameRates[i]))
        status='stay'
        
    if status=='next_frame':
        i+=1
        cv2.setTrackbarPos('Frame','image',i)
        cv2.setTrackbarPos('Time', 'image', int(resetTimeStamps[i])-int(tsLag))
        cv2.setTrackbarPos('Rate', 'image', int(frameRates[i]))
        status='stay'
        
    if status=='slow':
        #frame_rate = max(frame_rate - 5, 0)
        displayFrameRate = 10
        cv2.setTrackbarPos('Rate', 'image', displayFrameRate)
        status='play'
        
    if status=='fast':
        #frame_rate = min(100,frame_rate+5)
        displayFrameRate = 30
        cv2.setTrackbarPos('Rate', 'image', displayFrameRate)
        status='play'
        
    if status=='snap':
        cv2.imwrite(video.split('/')[-1].split('.')[0]+"Snap_"+str(i)+".jpg",im)
        print ("Snap of Frame",i,"Taken!")
        status='stay'
        status='play'
        


  except KeyError:
      print ("Invalid Key was pressed")
      cv2.destroyAllWindows()