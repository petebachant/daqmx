# -*- coding: utf-8 -*-
"""
Created on Mon Sep 02 13:42:35 2013

@author: Pete

Create objects for DAQmx tasks
"""
from __future__ import print_function, division
import daqmx
import numpy as np
from daqmx import channels

class Task(object):
    """DAQmx class object. Note that counter input tasks can only have one
    channel per task."""
    def __init__(self, name=""):
        self.name = name
        self.handle = daqmx.TaskHandle()
        daqmx.CreateTask(name.encode(), self.handle)
        self.sample_rate = 100.0
        self.timeout = 10.0 
        self.samples_per_channel = 10
        self.channels = []
        self.sample_clock_source = ""
        self.sample_clock_active_edge = "rising"
        self.sample_mode = "continuous samples"
        self.sample_clock_configured = False
        self.fillmode = "group by channel"
        self.task_type = ""
        
    def create_channel(self):
        """Creates and returns a channel object."""
        return channels.Channel()        
        
    def add_channel(self, channel):
        """Add existing channel object to channels dict."""
        self.channels.append(channel)
        phys_chan = channel.physical_channel.encode()
        name = channel.name.encode()
        term_conf = daqmx.parameters[channel.terminal_config]
        maxval = channel.maxval
        minval = channel.minval
        units = daqmx.parameters[channel.units]
        cust_scale_name = channel.custom_scale_name
        if cust_scale_name:
            units = daqmx.Val_FromCustomScale
        if channel.channel_type.lower() == "analog input":
            daqmx.CreateAIVoltageChan(self.handle, phys_chan, name, term_conf,
                                      minval, maxval, units, cust_scale_name)
            self.task_type = "analog input"
        
    def configure_sample_clock(self, sample_clock_source=None,
                               sample_rate=None,
                               sample_clock_active_edge=None,
                               sample_mode=None,
                               samples_per_channel=None):
        """Configures sample clock timing for task."""
        if sample_clock_source:
            self.sample_clock_source = sample_clock_source
        if sample_rate:
            self.sample_rate = sample_rate
        if sample_clock_active_edge:
            self.sample_clock_active_edge = sample_clock_active_edge
        if sample_mode:
            self.sample_mode = sample_mode
        if samples_per_channel:
            self.samples_per_channel = samples_per_channel
        sample_mode = daqmx.parameters[self.sample_mode]
        sample_clock_active_edge = daqmx.parameters[self.sample_clock_active_edge]
        daqmx.CfgSampClkTiming(self.handle, 
                               self.sample_clock_source, 
                               self.sample_rate, 
                               sample_clock_active_edge, 
                               sample_mode, 
                               self.samples_per_channel)
        self.sample_clock_configured = True
        
    def read(self):
        """Reads from the channels in the task."""
        array_size_samps = self.sample_rate*self.samples_per_channel
        fillmode = daqmx.parameters[self.fillmode]
        if self.task_type == "analog input":
            self.data, self.samples_per_channel_received = daqmx.ReadAnalogF64(
                    self.handle, self.samples_per_channel, self.timeout, 
                    fillmode, array_size_samps, len(self.channels))
                               
    def check(self, verbose=False):
        """Checks that all channel types in task are the same."""
        chantype = self.channels[0].channel_type
        passed = True
        for chan in self.channels:
            if chan.channel_type != chantype:
                passed = False
        if passed:
            if verbose:
                print("Channels are all the same type")
        else:
            if verbose:
                print("Channels are not all the same type")
        return passed
        
    def start(self):
        if self.check():
            if not self.sample_clock_configured:
                self.configure_sample_clock()
            daqmx.StartTask(self.handle)
        else:
            raise RuntimeError("Cannot start task because it has mixed channel types")

    def stop(self):
        daqmx.StopTask(self.handle)
        
    def clear(self):
        daqmx.ClearTask(self.handle)


def test_task():
    import time
    task = Task()
    c = daqmx.channels.AnalogInputChannel()
    c.physical_channel = "Dev1/ai0"
    task.add_channel(c)
    task.check(verbose=True)
    task.start()
    t0 = time.time()
    while time.time() - t0 < 3:
        time.sleep(1/task.sample_rate*10)
        task.read()
        print(task.samples_per_channel_received)
        print(task.data)
    task.stop()
    task.clear()


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
            print("Status", status.value)
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

if __name__ == "__main__":
    test_task()
