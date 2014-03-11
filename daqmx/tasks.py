# -*- coding: utf-8 -*-
"""
Created on Mon Sep 02 13:42:35 2013

@author: Pete

Create objects for DAQmx tasks
"""
import time
import daqmx
import numpy as np

class AnalogInput(object):
    def __init__(self):
	    pass

class AnalogOutput(object):
    pass
	
class CounterInput(object):
    pass
	
class CounterOutput(object):
    pass
	
class DigitalInput(object):
    pass
	
class DigitalOutput(object):
    pass

class GlobalVirtualAnalogInput(object):
    """Create an analog input task based on a global virtual channel."""
    def __init__(self, global_channels):
        self.global_channels = global_channels        
        self.taskhandle = daqmx.TaskHandle()
        daqmx.CreateTask("", self.taskhandle)
        daqmx.AddGlobalChansToTask(self.taskhandle, self.global_channels)
        self.channel_info = {}
        
        # Create empty dictionary for data
        # and add channel information to metadata
        for channel_name in global_channels:
            self.data[channel_name] = np.array([])
            self.channel_info[channel_name] = {}
            scale = daqmx.GetAICustomScaleName(self.taskhandle, channel_name)
            self.channel_info[channel_name]["Scale name"] = scale
            self.channel_info[channel_name]["Scale slope"] = \
            daqmx.GetScaleLinSlope(scale)
            self.channel_info[channel_name]["Scale y-intercept"] = \
            daqmx.GetScaleLinYIntercept(scale)
            self.chaninfo[channel_name]["Scaled units"] = \
            daqmx.GetScaleScaledUnits(scale)
            self.chaninfo[channel_name]["Prescaled units"] = \
            daqmx.GetScalePreScaledUnits(scale)
            
    def configsampleclock(self, rate, source):
        self.sr = rate
        pass
    
    def start(self):
        """Implement all the callback stuff here."""
        # Callback code from PyDAQmx
        class MyList(list):
            pass
        
        # List where the data are stored
        data = MyList()
        id_data = daqmx.create_callbackdata_id(data)
        
        # Function that is called every N callback
        def EveryNCallback_py(taskHandle, everyNsamplesEventType, nSamples, 
                              callbackData_ptr):          
            callbackdata = daqmx.get_callbackdata_from_id(callbackData_ptr)
            data, npoints = daqmx.ReadAnalogF64(taskHandle, int(self.sr/10), 
                    10.0, daqmx.Val_GroupByChannel, int(self.sr/10), 
                    len(self.analogchans))
            callbackdata.extend(data.tolist())
            
            for n in xrange(len(self.global_channels)):
                self.data[self.global_channels[n]] = np.append(
                        self.data[self.global_channels[n]], data[:,n], axis=0)
            return 0 # The function should return an integer
            
        # Convert the python callback function to a CFunction
        EveryNCallback = daqmx.EveryNSamplesEventCallbackPtr(EveryNCallback_py)
        daqmx.RegisterEveryNSamplesEvent(self.taskhandle, 
                daqmx.Val_Acquired_Into_Buffer, int(self.sr/10), 0, 
                EveryNCallback, id_data)    
        def DoneCallback_py(taskHandle, status, callbackData_ptr):
            print "Status", status.value
            return 0
        DoneCallback = daqmx.DoneEventCallbackPtr(DoneCallback_py)
        daqmx.RegisterDoneEvent(self.taskhandle, 0, DoneCallback, None) 

        # Start the task
        daqmx.StartTask(self.taskhandle)
        
        # Keep the acquisition going until task it cleared
        while True:
            pass        
        
    def stop(self):
        daqmx.StopTask(self.taskhandle)
        
    def clear(self):
        daqmx.ClearTask(self.taskhandle)
		
class GlobalVirtualCounterInput(object):
    pass