# -*- coding: utf-8 -*-
"""
Created on Fri Jun 07 12:16:31 2013

@author: Pete
"""

from daqmx import daqmx
import numpy as np
from numpy import pi
import time

def main():
    taskHandle = daqmx.TaskHandle()
    daqmx.CreateTask("", taskHandle)
    
    physicalChannel = "Dev1/ao0"
    
    t = np.linspace(0, 2*pi, 1000)
    data = 2*np.sin(t)
    
    daqmx.CreateAOVoltageChan(taskHandle, physicalChannel, "", 
                              -10.0, 10.0, daqmx.Val_Volts, None)
                              
    daqmx.CfgSampClkTiming(taskHandle, "", 100.0, daqmx.Val_Rising, 
                           daqmx.Val_ContSamps, 1000)
                           
    written = daqmx.WriteAnalogF64(taskHandle, 1000, 0, 10.0, 
                                   daqmx.Val_GroupByChannel, data)
                                  
    daqmx.StartTask(taskHandle)
    
    for n in range(100):
        time.sleep(0.3)
        print written, "samples written"
    
    daqmx.StopTask(taskHandle)
    daqmx.ClearTask(taskHandle)
    
if __name__ == "__main__":
    main()