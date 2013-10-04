# -*- coding: utf-8 -*-
"""
Created on Fri Jun 07 12:58:41 2013

@author: Pete
"""
import daqmx
import numpy as np
import matplotlib.pyplot as plt
import time

filename = "Data/test.npy"
np.save(filename, np.array([]))

numperiods = 3
period = 2.0
buffsize = 2000
sr = buffsize/period

t = np.linspace(0, 4*np.pi, buffsize)
dataw = 2*np.sin(t) #+ 0.5*np.random.random(len(t))


AItaskHandle = daqmx.TaskHandle()
AOtaskHandle = daqmx.TaskHandle()



daqmx.CreateTask("", AItaskHandle)
daqmx.CreateAIVoltageChan(AItaskHandle, "Dev1/ai1", "", daqmx.Val_Diff,
                          -10.0, 10.0, daqmx.Val_Volts, None)
daqmx.CfgSampClkTiming(AItaskHandle, "", sr, daqmx.Val_Rising, 
                       daqmx.Val_ContSamps, buffsize)
trigName = daqmx.GetTerminalNameWithDevPrefix(AItaskHandle, "ai/StartTrigger")




daqmx.CreateTask("", AOtaskHandle)
daqmx.CreateAOVoltageChan(AOtaskHandle, "Dev1/ao0", "", 
                          -10.0, 10.0, daqmx.Val_Volts, None)
daqmx.CfgSampClkTiming(AOtaskHandle, "", sr/2, daqmx.Val_Rising, 
                       daqmx.Val_ContSamps, buffsize)
daqmx.CfgDigEdgeStartTrig(AOtaskHandle, trigName, daqmx.Val_Rising)



class MyList(list):
    pass

# list where the data are stored
data = MyList()
id_data = daqmx.create_callbackdata_id(data)

def EveryNCallback_py(taskHandle, everyNsamplesEventType, nSamples, 
                      callbackData_ptr):
                          
    callbackdata = daqmx.get_callbackdata_from_id(callbackData_ptr)
    
    data, npoints = daqmx.ReadAnalogF64(taskHandle, buffsize, 10.0, 
                                        daqmx.Val_GroupByChannel, buffsize, 1)
                       
    callbackdata.extend(data.tolist())
    print "Acquired %d samples"%len(data)
    saved_data = np.load(filename)
    new_saved_data = np.append(saved_data, np.asarray(data))
    np.save(filename, new_saved_data)
    return 0 # The function should return an integer
    
# Convert the python function to a CFunction
EveryNCallback = daqmx.EveryNSamplesEventCallbackPtr(EveryNCallback_py)

daqmx.RegisterEveryNSamplesEvent(AItaskHandle,daqmx.Val_Acquired_Into_Buffer,
                                 buffsize, 0, EveryNCallback, id_data)
    



def DoneCallback_py(taskHandle, status, callbackData_ptr):
    print "Status", status.value
    return 0
    
DoneCallback = daqmx.DoneEventCallbackPtr(DoneCallback_py)

daqmx.RegisterDoneEvent(AItaskHandle, 0, DoneCallback, None)


written = daqmx.WriteAnalogF64(AOtaskHandle, buffsize, False, 10.0, 
                               daqmx.Val_GroupByChannel, dataw)
                               
                               
                     
daqmx.StartTask(AOtaskHandle)
daqmx.StartTask(AItaskHandle)


t0 = time.time()
elapsed = 0.0

while elapsed < period*numperiods:
    elapsed = time.time() - t0


daqmx.StopTask(AItaskHandle)
daqmx.ClearTask(AItaskHandle)
daqmx.StopTask(AOtaskHandle)
daqmx.ClearTask(AOtaskHandle)

plt.close('all')
t = np.arange(0, 1/sr*len(data), 1/sr)
plt.plot(t, data)
plt.xlabel("t (s)")
plt.hold(True)
saved_data = np.load(filename)
plt.plot(t, saved_data, '--r')