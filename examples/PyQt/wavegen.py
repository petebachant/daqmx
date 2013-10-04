# -*- coding: utf-8 -*-
"""
Created on Fri Jun 07 12:16:31 2013

@author: Pete
"""

import daqmx
import numpy as np
from numpy import pi
import time

def main(period):
    taskHandle = daqmx.TaskHandle()
    daqmx.CreateTask("", taskHandle)
    
    physicalChannel = "Dev1/ao0"
    
    t = np.linspace(0, 2*pi/period, 1000)
    data = 2*np.sin(t)
    
    daqmx.CreateAOVoltageChan(taskHandle, physicalChannel, "", 
                              -10.0, 10.0, daqmx.Val_Volts, None)
                              
    daqmx.CfgSampClkTiming(taskHandle, "", 1000.0, daqmx.Val_Rising, 
                           daqmx.Val_ContSamps, 1000)
                           
    daqmx.WriteAnalogF64(taskHandle, 1000, 0, 10.0, 
                         daqmx.Val_GroupByChannel, data)
                                  
    daqmx.StartTask(taskHandle)
    
    for n in range(100):
        time.sleep(0.3)
    
    daqmx.StopTask(taskHandle)
    daqmx.ClearTask(taskHandle)
    
if __name__ == "__main__":
    period = 1
    main(period)