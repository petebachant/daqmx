# -*- coding: utf-8 -*-
"""
Created on Fri Jun 07 12:58:41 2013

@author: Pete
"""
import daqmx
import numpy as np
from numpy import pi
import time
import matplotlib.pyplot as plt

AItaskHandle = daqmx.TaskHandle()
AOtaskHandle = daqmx.TaskHandle()

daqmx.CreateTask("", AItaskHandle)
daqmx.CreateTask("", AOtaskHandle)

sr = 100.0

t = np.linspace(0, 100.0, 1000)
data = 2*np.sin(t)

daqmx.CreateAOVoltageChan(AOtaskHandle, "Dev1/ao0", "", 
                          -10.0, 10.0, daqmx.Val_Volts, None)
                          
daqmx.CfgSampClkTiming(AOtaskHandle, "", sr, daqmx.Val_Rising, 
                       daqmx.Val_ContSamps, 1000)
                       
daqmx.CreateAIVoltageChan(AItaskHandle, "Dev1/ai1", "", daqmx.Val_Diff,
                          -10.0, 10.0, daqmx.Val_Volts, None)
                              
                              
daqmx.CfgSampClkTiming(AItaskHandle, "", sr, daqmx.Val_Rising, 
                       daqmx.Val_ContSamps, 1000)
                       

written = daqmx.WriteAnalogF64(AOtaskHandle, 1000, 0, 10.0, 
                               daqmx.Val_GroupByChannel, data)
                               
                               
dataread, nread = daqmx.ReadAnalogF64(AItaskHandle, 1000, 10.0, 
                                      daqmx.Val_GroupByChannel, 1000, 1)                               

                              
daqmx.StartTask(AOtaskHandle)
daqmx.StartTask(AItaskHandle)


print written, "samples written"
print nread, "samples read"

plt.plot(dataread)


daqmx.StopTask(AItaskHandle)
daqmx.ClearTask(AItaskHandle)
daqmx.StopTask(AOtaskHandle)
daqmx.ClearTask(AOtaskHandle)