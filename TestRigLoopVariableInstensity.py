# -*- coding: utf-8 -*-
"""
Created on Thu Jan 13 14:45:19 2022

Read input from AI0 (differntial) coming from DO (ephy rig)
When TTL kicks in, writes a TTL Wave to AO0 in order to modulate the light source
Loops as many times as needed, or as many intensities are written 

@author: klab
"""
#---------------------FILL PARAMETERS HERE-------------------------------------
#---------------------ALL TIME VALUES ARE IN SECONDS---------------------------
#---------------------INTENSITIES ARE IN VOLTS---------------------------------
#intensities = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
intensities = [0.4, 0.8, 0.2, 0.1, 1.0, 0.9, 0.5, 0.8, 0.3, 0.7,
               0.4, 0.8, 0.2, 0.1, 1.0, 0.9, 0.5, 0.8, 0.3, 0.7,
               0.4, 0.8, 0.2, 0.1, 1.0, 0.9, 0.5, 0.8, 0.3, 0.7]
waveDuration = 1
samplingRateInWave = 0.001
stimOnsetInWave = 0
pulseDurationInWave = 0.005
lowStateInWave = 0
repeatPulses = 0
freqPulses = 25

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


if __name__ == '__main__':
    
    import nidaqmx 
    from nidaqmx.constants import TerminalConfiguration
    import time
    
    #Sampling rate
    Ts = samplingRateInWave
    
    #Initiate reading in AI0
    #Read task : read voltage from Analog Input 0 (ai0)
    taskRead = nidaqmx.Task()
    taskRead.ai_channels.add_ai_voltage_chan(physical_channel='Dev2/ai0', 
                                             terminal_config = TerminalConfiguration.DIFFERENTIAL)
    
    
    #Initiate AO0 write
    #Write task : set voltage to Analog Output 0 (ao0)
    taskWrite = nidaqmx.Task()
    taskWrite.ao_channels.add_ao_voltage_chan(physical_channel='Dev2/ao0',
                                              name_to_assign_to_channel='mychannel',
                                              min_val=0,
                                              max_val=10)

    
    for stim in intensities:
        #Start the tasks        
        taskRead.start()
        taskWrite.start()

        #Create stim wave
        stimTime, stimWave = TTLsigWave(totalDuration=waveDuration,
                                        samplingrate=Ts,
                                        stimOnset=stimOnsetInWave,
                                        pulseDuration=pulseDurationInWave,
                                        lowState=lowStateInWave,
                                        highState=stim,
                                        repeat=repeatPulses,
                                        freq=freqPulses)
        
            
        while True:
            
            val = taskRead.read()
            print(val)
            
            if val >= 4.0:
                
                for i in range(len(stimWave)):
                    taskWrite.write(stimWave[i])
                    time.sleep(Ts)
                    
                taskWrite.stop()

                
                taskRead.stop()

                    
                break
            
    taskRead.close()
    taskWrite.close()
        

    
    
#     for k in range(len(TTL)): 
        
#         if TTL[k] == 0:
#             taskDO.write(False)

#         else: 
#             taskDO.write(True)

#             val = taskRead.read()
            
#             if val > 1.0: 
                
#                 for i in range(len(stimWave)):
                    
#                     taskWrite.write(stimWave[i])
                    
#                     time.sleep(Ts)
                    
#                 break
                
#             else:
#                 continue
            
#         time.sleep(Ts)
        
#     taskWrite.stop()
#     taskWrite.close()
    
#     taskDO.stop()
#     taskDO.close()
    
#     taskRead.stop()
#     taskRead.close()
        
        

# volts = [0,1,2,3,4,5]
# watts = [0,1.7,3.1,4.2,5.3,6.9]

# import matplotlib.pyplot as plt
# plt.figure()
# plt.plot(volts, watts)
# plt.scatter(volts, watts)
# plt.xlabel('Input (V)'); plt.ylabel('Power (mW)')
# plt.title('400microns 450nm')
        
    
    
    
