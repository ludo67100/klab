# -*- coding: utf-8 -*-
"""
Created on Mon Feb 21 17:25:31 2022

@author: klab
"""

import matplotlib.pyplot as plt 
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams.update({'font.size': 7})
import pandas as pd 
import numpy as np
import neo
import quantities as pq
from elephant import statistics
import numpy as np
from scipy.optimize import curve_fit
import os
from scipy import stats

#In s
binSize = 0.100
baselineDuration = 1

CELLS_TO_COMPUTE = ['01262022_Cell2','01262022_Cell3',
                    '01272022_Cell1',
                    '02022022_Cell2',
                    '02032022_Cell2','02032022_Cell3','02032022_Cell4',
                    '02092022_Cell3']

cell = '02092022_Cell3'

timeStamps = [-6,-4,-2,
              2,4,6,
              8,10,12,
              14,16,18,
              20,22,24,
              26,28,30
              ] #In minutes

mainDirectory = 'D:/00_KLAB/ANALYSIS/NE_Project/GainExtraCell/Atoh1/NE_Application'

saveDir = 'D:/00_KLAB/ANALYSIS/NE_Project/GainExtraCell/Atoh1/NE_Application/Analyzed/No_Convolution_Ind_Slopes_Vs_Average_Baseline'



def logistic4(x, A, B, C, D):
    #4PL lgoistic equation
    return ((A-D)/(1.0+(np.power(x/C,B)))) + D

def lineReg(x,a,b):
    return a*x+b

def strToFloat(listOfStims):
    '''
    Converts a list of mixed inpunts (int floats str) to numerical values only
    '''
    newList = []
    for mambo in listOfStims:
        if type(mambo) == str:
            newList.append(float(mambo[:-2]))
        else:
            newList.append(mambo)
    return np.array(newList)

def InstFR(spikesInBin):
    '''
    computes inst. firing freq in spike times
    '''
    a = np.array(spikesInBin[1:])
    b = np.array(spikesInBin[:-1])
    
    return 1./(a-b)

if __name__ == '__main__': 
    
    mainDataFolder = '{}/{}'.format(mainDirectory,cell)
    
    cellID = cell
    
    
    # Get the list of all files in directory tree at given path
    listOfFiles = list()
    for (dirpath, dirnames, filenames) in os.walk(mainDataFolder):
        listOfFiles += [os.path.join(dirpath, file) for file in filenames if 'spikeTimes.xlsx' in file]
        
    maxFR, PrePostFiringRatio, AmountOfExtraSpikes, BasalFiringRate, RangeOfStim = [],[],[],[],[]
        
    for file in listOfFiles:
    
        df = pd.read_excel(file, header=0,index_col=0)
        
        #global appends
        avgFR, sdFR = [], []
        avgCount, sdCount = [], []
        stim = []
        

        #Iterate over columns
        seq = np.reshape(df.columns, (-1,3))
        
        rasterFig, rasterAx = plt.subplots(seq.shape[0],seq.shape[1],sharex=True,sharey=True, figsize=(5,8))
        rasterFig.suptitle(file.split('/')[-1].split('\\')[-1])
        
        maxFiringRate, firingRatio, ExtraSpikes, basalFiringRate, stimRange = [],[],[],[],[]
        
        for sequence, seqIndx in zip(seq, range(seq.shape[0])):
           
            tempFiringRate, tempFiringRatio, tempExtraSpike, tempBasalFiringRate, tempStim = [],[],[],[],[]
            
            for trial,trialIndx in zip(sequence,range(len(sequence))): 
                
                tempStim.append(trial)
                
                #Some of the files do not have a 0.6 step 
                spikeTimes = df[trial].dropna().values
                
                spikeTrain = neo.SpikeTrain(spikeTimes*pq.s, t_start=-1.5,t_stop=3.5)
                
                #PSTH        
                hist = statistics.time_histogram(spikeTrain, binSize/2*pq.s)
                
                # ax[seqIndx,trialIndx].bar(hist.times.flatten(), 
                #                            hist.magnitude.flatten(), 
                #                            width=0.1)
                rasterAx[seqIndx,trialIndx].bar(hist.times.flatten(), 
                                                hist.magnitude.flatten(), 
                                                width=0.05,color='0.40', 
                                                align='edge')
        
                rasterAx[seqIndx,trialIndx].axvspan(0,0.002, color='skyblue', alpha=0.5)
                rasterAx[seqIndx,trialIndx].set_xlim(-0.200,0.200)
                
                #Add lables in plots
                if trialIndx == 0:
                    rasterAx[seqIndx,trialIndx].set_ylabel('Stim= {}'.format(trial))
                    
                if seqIndx == 0:
                    rasterAx[seqIndx,trialIndx].set_title('Trial #{}'.format(trialIndx+1))
                
                #Evoked and Basal Max Firing Rate
                PreInstantEvokedFR = InstFR([x for x in spikeTimes if -1*baselineDuration < x < 0])
                PostInstantEvokedFR = InstFR([x for x in spikeTimes if 0 < x < binSize])
                
                try:
                    maxPreFR = np.nanmean(PreInstantEvokedFR)
                    maxPostFR = max(PostInstantEvokedFR)
            
                    #Extra Spikes
                    extraSpikes = len([x for x in spikeTimes if 0 < x < binSize]) - len([x for x in spikeTimes if -binSize < x < 0])
                    
                    #Append for temp
                    tempFiringRate.append(maxPostFR)
                    tempFiringRatio.append(maxPostFR/maxPreFR)
                    tempExtraSpike.append(extraSpikes)
                    tempBasalFiringRate.append(maxPreFR)
                    
                except:
                    #Append np.nan for temp
                    tempFiringRate.append(np.nan)
                    tempFiringRatio.append(np.nan)
                    tempExtraSpike.append(np.nan)
                    tempBasalFiringRate.append(np.nan)
                    
                
            #Append in main list
            maxFiringRate.append(tempFiringRate)
            firingRatio.append(tempFiringRatio)
            ExtraSpikes.append(tempExtraSpike)
            basalFiringRate.append(tempBasalFiringRate)
            stimRange.append(tempStim[0])
            
        #Global append
        maxFR.append(maxFiringRate)
        PrePostFiringRatio.append(firingRatio)
        AmountOfExtraSpikes.append(ExtraSpikes)
        BasalFiringRate.append(basalFiringRate)
        RangeOfStim.append(stimRange)
        
        #Save Raterplot
        rasterFig.savefig('{}/{}_{}.pdf'.format(saveDir, cellID, file.split('/')[-1].split('\\')[-1].split('_')[2].split('.')[0]))
        rasterFig.savefig('{}/{}_{}.png'.format(saveDir, cellID, file.split('/')[-1].split('\\')[-1].split('_')[2].split('.')[0]))
            
            
    #Build dataset-----------------------------------------------------------------
    maxEvokedFireRate = np.asarray(maxFR)
    FiringRatio = np.asarray(PrePostFiringRatio)
    NumOfExtraSpikes = np.asarray(AmountOfExtraSpikes)
    baselineFiringRate = np.asarray(BasalFiringRate)
    listOfRange = strToFloat(RangeOfStim[0])
    
    
    variables = [np.hstack(([maxEvokedFireRate[x,:,:] for x in range(maxEvokedFireRate.shape[0])])),
                 np.hstack(([FiringRatio[x,:,:] for x in range(FiringRatio.shape[0])])),
                 np.hstack(([NumOfExtraSpikes[x,:,:] for x in range(NumOfExtraSpikes.shape[0])]))]
    
    var_labels = ['Max. Evoked\n Firing Rate','Pre/Post\n Firing rate Ratio', 'Extra Spikes']
    saveLabels = ['MaximumEvokedFiringRate', 'prepostFiringRateRatio', 'ExtraSpikes']
    
    regressionFig, regressionAx = plt.subplots(len(variables),variables[0].shape[1],sharex=True, sharey=False, figsize=(19,4))
    regressionFig.suptitle('{} \nRegression lines'.format(mainDataFolder.split('/')[-1]))
    mainFig, mainAx = plt.subplots(len(variables),1, sharex=True)
    mainFig.suptitle('{} \nLinear regression Slopes'.format(mainDataFolder.split('/')[-1]))
    
    
    #Compute regression lines and plot
    #All variables are stored in a loop 
    for i in range(len(variables)): 
        
        data = variables[i]
        mainAx[i].set_ylabel(var_labels[i])
        #Save input Dfs
        inputDf = pd.DataFrame(data, index=listOfRange, columns=timeStamps)
        inputDf.to_excel('{}/{}_{}.xlsx'.format(saveDir,cellID,saveLabels[i]))
        
        #Append regression params in a list
        regStore = []
        
        for j in range(data.shape[1]):
        
            x = listOfRange
            y = variables[i][:,j]
            
            #Get rid of eventual nans
            valid = ~(np.isnan(x) | np.isnan(y))
            popt, pcov = curve_fit(lineReg, x[valid], y[valid])
            
            lineregressStat = stats.linregress(x[valid],y[valid])
            
            if j == 0:
                regressionAx[i,j].set_ylabel(var_labels[i])
                
            if i == len(variables)-1:
                regressionAx[i,j].set_xlabel('Stim. Value [UA]')
                mainAx[i].set_xlabel('Time from application (min)')
                
            
            regressionAx[i,j].scatter(x, y, alpha=0.5)
            regressionAx[i,j].set_ylim(min(variables[i].ravel())/1.2,max(variables[i].ravel())*1.2)
            regressionAx[i,j].plot(x, lineReg(x,popt[0],popt[1]))
            regressionAx[i,j].set_title('t={} | r={}'.format(timeStamps[j],round(lineregressStat[2],2)))
            mainAx[i].scatter(timeStamps[j], popt[0])
            
            
            regStore.append([lineregressStat.slope,
                             lineregressStat.intercept,
                             lineregressStat.rvalue,
                             lineregressStat.pvalue,
                             lineregressStat.stderr,
                             lineregressStat.intercept_stderr])
            
            
        outPutDf = pd.DataFrame(regStore, 
                                index=timeStamps, 
                                columns=['slope','intercept','rvalue','pvalue','slope_std','intercept_std']).T
        
        outPutDf.to_excel('{}/{}_{}_linearRegResult.xlsx'.format(saveDir,cellID,saveLabels[i]))
            
    
    #tight layout
    regressionFig.tight_layout()
    
    #Save plots
    mainFig.savefig('{}/{}_SlopeTimeCourse.pdf'.format(saveDir, cellID))
    mainFig.savefig('{}/{}_SlopeTimeCourse.png'.format(saveDir, cellID))     
    
    regressionFig.savefig('{}/{}_RegressionLines.pdf'.format(saveDir, cellID))  
    regressionFig.savefig('{}/{}_RegressionLines.png'.format(saveDir, cellID))    
    
    print('{} has been computed'.format(cell))
            

            
                    
    