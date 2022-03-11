# -*- coding: utf-8 -*-
"""
Created on Wed Mar  9 15:47:08 2022

@author: klab
"""

import matplotlib.pyplot as plt 
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams.update({'font.size': 7})
import pandas as pd 
import json 
import numpy as np 
import datetime
from matplotlib.pyplot import cm



#TODO 
#Add iteration over files 

def timeStringToSeconds(timestring):
    '''
    returns total time in seconds from h:m:s string
    '''
    hours = int(timestring.split(':')[0])*3600
    minutes = int(timestring.split(':')[1])*60
    seconds = float(timestring.split(':')[2])
    return hours+minutes+seconds

#file = 'D:/00_KLAB/IBLRig/raw_behavior_data/_iblrig_taskData.raw.jsonable'
file = 'D:/00_KLAB/IBLRig/006/raw_behavior_data/_iblrig_taskData.raw.jsonable'

f = open(file)
fig, ax = plt.subplots(3,1, sharex=True, figsize=(5,9))
fig.suptitle(file)
ax[0].set_xlabel('Trial #'); ax[0].set_ylabel('PortIn Sampling [Hz]')

numericalData = []
listOfEvents = []
for line in f: 
    print()

    trialDict = json.loads(line)
    
    #Collect data-------------------------------------------------------------
        #Trial info
    trialIndex = trialDict['trial_num']
    initialPosition = trialDict['position']
    
        #Time
    initialTime = trialDict['init_datetime']
    elapsedTime = trialDict['elapsed_time']
    responseTime = trialDict['response_time']
    
    trialStartTimeStamp = trialDict['behavior_data']['Trial start timestamp']
    trialStopTimeStamp = trialDict['behavior_data']['Trial end timestamp']
    
    sessionInitialTime = trialDict['init_datetime']
    
    quiescentPeriod = trialDict['quiescent_period']
    
        #Directions
    thresholdEvents = trialDict['threshold_events_dict']
    
    rewardEvent = trialDict['event_reward']
    rewardThreshold = int(list(thresholdEvents.keys())[list(thresholdEvents.values()).index(rewardEvent)])
    
    errorEvent = trialDict['event_error']
    errorThreshold = int(list(thresholdEvents.keys())[list(thresholdEvents.values()).index(errorEvent)])
    
        #Outcome
    if responseTime >= trialDict['response_window']:
        trialOut = 0
    else: 
        #Mouse is correct
        if trialDict['trial_correct'] == True:
            trialOut = 1
    
        #Mouse is wrong
        elif trialDict['trial_correct'] == False:
            trialOut = -1
            
    deliveredWater = trialDict['water_delivered']
    
    #Event time stamps 
    try:
        eventDf = pd.DataFrame.from_dict(trialDict['behavior_data']['States timestamps'])
    
    #For some reasons, sometimes some parameters are encoded a every time points instead of just on/off states
    except ValueError: 
        for key in trialDict['behavior_data']['States timestamps']:
            if len(trialDict['behavior_data']['States timestamps'][key]) < 2: 
                continue
            else: 
                newVal = [trialDict['behavior_data']['States timestamps'][key][0][0],
                          trialDict['behavior_data']['States timestamps'][key][-1][-1]]
                                
                trialDict['behavior_data']['States timestamps'][key] = newVal
                
    #Turn eventDf in one value per column 
    splittedValues, splittedColumns = [],[]

    for col in eventDf: 
        splittedValues.append(eventDf[col].values[0][0])
        splittedValues.append(eventDf[col].values[0][1])
        
        splittedColumns.append('{}_ON'.format(col))
        splittedColumns.append('{}_OFF'.format(col))
        
    UpdatedEventDf = pd.DataFrame(splittedValues, index=splittedColumns, columns=[trialIndex]).T

    #Append in list-----------------------------------------------------------
    numericalData.append([trialIndex,
                          initialPosition,
                          trialStartTimeStamp,
                          quiescentPeriod,
                          trialStopTimeStamp,
                          rewardThreshold,
                          errorThreshold,
                          timeStringToSeconds(elapsedTime),
                          trialOut,
                          deliveredWater,
                          sessionInitialTime,
                          elapsedTime, 
                          responseTime])
    
    listOfEvents.append(UpdatedEventDf)

#format excel file 
cols = ['trial index', 'initial position','trial start timestamp (s)','quiescent period', 'trial stop timestamp (s)',
        'reward position','error position','elapsed time (s)',
        'trial outcome', 'delivered water','Session Init','elapsed time', 'responseTime']

df = pd.DataFrame(numericalData, columns=cols)

mainEventDf = pd.concat(listOfEvents, axis=0, ignore_index=True)

#df.to_excel('D:/00_KLAB/IBLRig/OUT/test.xlsx')
pd.concat((df, mainEventDf), axis=1, ignore_index=False).to_excel('D:/00_KLAB/IBLRig/OUT/test.xlsx')
    
ax[0].plot(df['trial outcome'], marker='o')
ax[0].set_xlabel('Trial #'); ax[0].set_ylabel('Trial Outcome \n[-1: error | 0:timeOut | 1:success]')

ax[1].plot(df['delivered water'], marker='o')
ax[1].set_xlabel('Trial #'); ax[1].set_ylabel('Reward Delivered (uL)')

ax[2].plot(df['elapsed time (s)'], marker='o')
ax[2].set_xlabel('Trial #'); ax[2].set_ylabel('elapsed time (seconds)')


plt.tight_layout()


#For later - unify with rotary encoder ########################################
# plt.figure(figsize=(16,6))
# plt.xlabel('Time in trial (seconds)')

# events = trialDict['behavior_data']['States timestamps']
# sortedEvents = {k: v for k, v in sorted(events.items(), key=lambda item: item[1])}

# color = cm.rainbow(np.linspace(0, 1, len(sortedEvents)))

# for k, i in zip(sortedEvents, range(len(sortedEvents))):
    
#     vals = sortedEvents[k]
    
#     if k == 'closed_loop':
#         continue
#     else:
#         plt.axvspan(xmin=vals[0][0], xmax=vals[0][1], ymin=0, ymax=1, color=color[i], label=k, alpha=0.5)
    

# plt.legend(loc='best')

    


# from dateutil import parser
# a = parser.parse(sessionInitialTime)  

# b = a + datetime.timedelta(seconds=trialStartTimeStamp)

# c = b + datetime.timedelta(seconds=trialStopTimeStamp)



#Check sampling rate of behavior data-------------------------------------
# PortIn = np.asarray(trialDict['behavior_data']['Events timestamps']['Port1In'])
# sampling_periods = PortIn[1:]-PortIn[:-1]
# sampling_rates = 1./sampling_periods
# ax[0].scatter(np.ones(len(np.unique(sampling_rates)))*trialIndex, np.unique(sampling_rates))

    
    
    
    
    
    

    