# -*- coding: utf-8 -*-
"""
Created on Fri Jun 07 00:29:49 2013

@author: Pete
"""
import daqmx
import time
import numpy as np

aiTaskHandle = daqmx.TaskHandle()
diTaskHandle = daqmx.TaskHandle()

daqmx.CreateTask("", aiTaskHandle)
daqmx.CreateAIVoltageChan(aiTaskHandle, "Dev1/ai0", "", daqmx.Val_Diff,
                          0.0, 10.0, daqmx.Val_Volts)
                          
daqmx.CfgSampClkTiming(aiTaskHandle, "", 100.0, daqmx.Val_Rising, 
                       daqmx.Val_ContSamps, 1000)
                       
trigname = daqmx.GetTerminalNameWithDevPrefix(aiTaskHandle, "ai/SampleClock")

daqmx.CreateTask("", diTaskHandle)
daqmx.CreateDIChan(diTaskHandle,"Dev1/port0","", daqmx.Val_ChanForAllLines)
daqmx.CfgSampClkTiming(diTaskHandle, trigname, 100.0, daqmx.Val_Rising,
                       daqmx.Val_ContSamps, 1000)
                       
daqmx.StartTask(diTaskHandle)
daqmx.StartTask(aiTaskHandle)

adata = daqmx.ReadAnalogF64(aiTaskHandle, 1000, 10.0,daqmx.Val_GroupByChannel,
                            1000, 1)
ddata = daqmx.ReadDigitalU32(diTaskHandle, 1000, 10.0, daqmx.Val_GroupByChannel,
                             1000, 1)
                             
print adata
print ddata

daqmx.StopTask(diTaskHandle)
daqmx.StopTask(aiTaskHandle)
daqmx.ClearTask(diTaskHandle)
daqmx.ClearTask(aiTaskHandle)