# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 11:39:47 2024

@author: ludo in klab
"""

#---------------------FILL PARAMETERS HERE-------------------------------------
#---------------------ALL TIME VALUES ARE IN SECONDS---------------------------
#---------------------INTENSITIES ARE IN VOLTS---------------------------------

#Size of the pulse in Volts
intensities = 5.0  

#Total duration of the train 
waveDuration = 3 

#5k is the max of the NiDaq
samplingRateInWave = 1/5000 

#Onset of the first stim in train 
stimOnsetInWave = 0 

#Duration of each pulse 
pulseDurationInWave = 0.001 

#Baseline voltage
lowStateInWave = 0 

#Baseline voltage
repeatPulses = 60

#Frequency of the pulses 
freqPulses = 20 

#Number of trials 
numTrial = 2 

#Times between trials 
interTrialInterval = 10 

#'Dev1/ao0' = laser / 'Dev1/ao1' =electric pulse
dev_chan = 'Dev1/ao0'



#TODO ADD superimpose channels 

#----------------------------------THE CODE------------------------------------
#------------------------------------------------------------------------------


def TTLsigWave(totalDuration=1, 
               samplingrate=0.0001, 
               stimOnset=0.5, 
               pulseDuration=0.001, 
               lowState=0, 
               highState=5, 
               repeat=4, 
               freq=20):
    '''
    Generates a TTL wave composed of n (1+repeat) squared pulses
    
    INPUT:
        totalDuration (int) : total duration of the wave in seconds
        samplingrate (float) : sampling rate of the wave
        stimOnset (float) : onset of stim in seconds
        pulseDuration (float) : duration on the pulses in seconds
        lowState / highState (int/int) : voltage in low and high state
        repeat (int) : number of pulse repeat
        freq (int) : frequency of the pulses
    OUTPUT: 
        TTLWave (array)
    '''

    #Check that Nyquist law is correct
    #assert samplingrate <= pulseDuration/2, 'sampling rate is too low compared to pulse duration (Nyquist)'

    #Define time and base wave
    import numpy as np
    timeVector = np.arange(0,totalDuration,samplingrate)
    wave = np.ones(len(timeVector))*lowState

    #If only one pulse
    if repeat == 0: 
        wave[np.where(timeVector>stimOnset)[0]] = highState
        wave[np.where(timeVector>stimOnset+pulseDuration)[0][1:]] = lowState

    #Add else for repeat stim 
    else: 
        #assert pulseDuration < 1./freq, 'Pulse duration > burst frequency'
        wave[np.where(timeVector>stimOnset)[0]] = highState
        wave[np.where(timeVector>stimOnset+pulseDuration)[0][1:]] = lowState

        for i in range(repeat): 
            factor = (1./freq)*(i+1)
            wave[np.where(timeVector>stimOnset+factor)[0]] = highState
            wave[np.where(timeVector>stimOnset+factor+pulseDuration)[0][1:]] = lowState


    return timeVector,wave


def make_plot(x, y, title): 
    from matplotlib import pyplot as plt
    
    
    fig, ax = plt.subplots(1,1)
    ax.plot(x, y)
    ax.set_xlabel('Time (s)'); ax.set_ylabel('Voltage (V)')
    ax.set_title('InterTrialInterval = {}s'.format(title))
    fig.canvas.flush_events()
    plt.draw()
    

#Create stim wave
stimTime, stimWave = TTLsigWave(totalDuration=waveDuration,
                                samplingrate=samplingRateInWave,
                                stimOnset=stimOnsetInWave,
                                pulseDuration=pulseDurationInWave,
                                lowState=lowStateInWave,
                                highState=intensities,
                                repeat=repeatPulses,
                                freq=freqPulses)



if __name__ == '__main__':
    
    print('Buffering')

    import nidaqmx 
    import time
    
    # ttlTime, ttlAmp = TTLsigWave(totalDuration=2, repeat=20)
    # fig, ax = plt.subplots(1,1)
    # ax.plot(ttlTime, ttlAmp)

    '''
    #Sampling rate
    Ts = samplingRateInWave

    #Initiate reading in AI0 #ONLY IF YOU NEED TO WAIT FOR TRIGGER, THEN AD WHILE LOOP WITH STATE
    #Read task : read voltage from Analog Input 0 (ai0)
    taskRead = nidaqmx.Task()
    taskRead.ai_channels.add_ai_voltage_chan(physical_channel='Dev1/ai0', 
                                             terminal_config = nidaqmx.constants.TerminalConfiguration.DIFFERENTIAL)

    '''
    
    for i in range(numTrial):
        
        print('----------- Trial #{}/{} -----------'.format(i+1, numTrial))

        #Initiate AO0 write
        #Write task : set voltage to Analog Output 0 (ao0)
        taskWrite = nidaqmx.Task()
        taskWrite.ao_channels.add_ao_voltage_chan(physical_channel=dev_chan,
                                                  name_to_assign_to_channel='mychannel',
                                                  min_val=0,
                                                  max_val=5)
    
        Ts = samplingRateInWave
    
        #Start the tasks        
        taskWrite.start()

        #Create stim wave
        stimTime, stimWave = TTLsigWave(totalDuration=waveDuration,
                                        samplingrate=Ts,
                                        stimOnset=stimOnsetInWave,
                                        pulseDuration=pulseDurationInWave,
                                        lowState=lowStateInWave,
                                        highState=intensities,
                                        repeat=repeatPulses,
                                        freq=freqPulses)
        if i ==0:
            make_plot(stimTime, stimWave, title=interTrialInterval)
        
        #Write the stim wave to DAQ
        print('Stim Started')
        taskWrite.write(stimWave)

        #Clear task to allow buffering of the next trial 
        taskWrite.stop()
        taskWrite.close()
        print('Stim Complete')
        
        #Intertrial time, the code will stop during this amount of time

        for i in range(interTrialInterval):
            time.sleep(1)
            print ('    Next trial in: {}s'.format(interTrialInterval-i-1))
        print('        Trial complete')
        print('')
        print('')

        #time.sleep(interTrialInterval)


    
