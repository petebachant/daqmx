# -*- coding: utf-8 -*-
"""
Created on Mon Sep 02 13:42:35 2013

@author: Pete

Create objects for DAQmx tasks
"""
from __future__ import print_function, division
import daqmx
import numpy as np
from . import channels
from PyDAQmx import Task as PyDaqMxTask
import pandas as pd
import os
import h5py

class Task(PyDaqMxTask):
    """DAQmx class object. Note that counter input tasks can only have one
    channel per task."""
    def __init__(self, name=""):
        PyDaqMxTask.__init__(self)
        self.name = name
        self.handle = daqmx.TaskHandle()
        self.TaskHandle = self.handle
        self.taskHandle = self.handle
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
        self.append_data = False
        self.autolog = False
        self.autotrim_limit = 100000 # Maximum number of samples to keep
        self.autotrim = False # Only applicable if appending data
        
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
        if channel.channel_type.lower() == "analog input voltage":
            daqmx.CreateAIVoltageChan(self.handle, phys_chan, name, term_conf,
                                      minval, maxval, units, cust_scale_name)
            self.task_type = "analog input"
        elif channel.channel_type.lower() == "analog input bridge":
            bridge_config = daqmx.parameters[channel.bridge_config]
            voltage_exc_source = daqmx.parameters[channel.voltage_exc_source]
            voltage_exc_value = channel.voltage_exc_value
            nominal_bridge_resistance = channel.nominal_bridge_resistance
            daqmx.CreateAIBridgeChan(self.handle, phys_chan, name, minval,
                                     maxval, units, bridge_config, voltage_exc_source,
                                     voltage_exc_value, nominal_bridge_resistance,
                                     cust_scale_name)
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
    
    def create_dataframe(self, time_array=True):
        self.data = pd.DataFrame()
        self.time_array = time_array
        if self.time_array:
            self.data["time"] = np.array([])
        for channel in self.channels:
            self.data[channel.name] = np.array([])
        
    def read(self):
        """Reads from the channels in the task."""
        array_size_samps = self.sample_rate*self.samples_per_channel
        fillmode = daqmx.parameters[self.fillmode]
        if self.task_type == "analog input":
            self.newdata, self.samples_per_channel_received = daqmx.ReadAnalogF64(
                    self.handle, self.samples_per_channel, self.timeout, 
                    fillmode, array_size_samps, len(self.channels))
        if self.append_data:
            self.newdf = pd.DataFrame()
            if self.time_array:
                newtime = np.arange(self.samples_per_channel_received + 1)/self.sample_rate
                if len(self.data["time"]) == 0:
                    self.newdf["time"] = newtime[:-1]
                else:
                    last_time = self.data["time"].values[-1]
                    newtime += last_time
                    self.newdf["time"] = newtime[1:]
            for n, channel in enumerate(self.channels):
                self.newdf[channel.name] = self.newdata[:,n]
            self.data = self.data.append(self.newdf, ignore_index=False)
            if self.autolog:
                self.do_autolog()
            if self.autotrim:
                self.autotrim_dataframe()
        return self.newdata, self.samples_per_channel_received
                    
    def auto_register_every_n_samples_event(self):
        """Will call a function every n samples."""
        self.AutoRegisterEveryNSamplesEvent(daqmx.Val_Acquired_Into_Buffer,
                                            self.samples_per_channel,0)
                                            
    def auto_register_done_event(self):
        self.AutoRegisterDoneEvent(0)
        
    def register_done_event(self):
        """Automatically registers done event similar to PyDAQmx."""
        def DoneCallback_py(taskHandle, status, callbackData_ptr):
            print("Status", status.value)
            return 0
        DoneCallback = daqmx.DoneEventCallbackPtr(DoneCallback_py)
        daqmx.RegisterDoneEvent(self.handle, 0, DoneCallback, None)
        
    def EveryNCallback(self):
        self.every_n_callback()
        return 0 # The function should return an integer

    def DoneCallback(self, status):
        print("Status", status.value)
        return 0 # The function should return an integer
        
    def setup_autologging(self, filename, time_array=True,
                          newfile=True):
        """Sets up channel to automatically stream data to file---either
        raw text, CSV, or HDF5, depending on filename"""
        self.autolog = True
        self.autolog_filename = filename
        self.autolog_filetype = self.autolog_filename.split(".")[-1].lower() 
        if not self.append_data:
            self.setup_append_data(time_array)
        if newfile and os.path.isfile(filename):
            os.remove(self.autolog_filename)
        if self.autolog_filetype in ["h5", "hdf5"]:
            self.autolog_file_object = h5py.File(filename, mode="a")
        elif self.autolog_filetype == "csv":
            self.autolog_file_object = open(filename, "a")
            self.data.to_csv(self.autolog_file_object, header=True, index=False)
        
    def do_autolog(self):
        """Automatically log data to disk, snipping off the oldest data
        from the arrays in the data dict."""
        data = self.newdf
        if self.autolog_filetype == "csv":
            data.to_csv(self.autolog_file_object, mode="a", index=False, 
                        header=False)
        elif self.autolog_filetype in ["h5", "hdf5"]:
            f = self.autolog_file_object
            for key, value in data.items():
                try:
                    oldval = f["data/" + key]
                    newval = np.append(oldval, value)
                    del f["data/" + key]
                except KeyError:
                    newval = value
                f["data/" + key] = newval

    def every_n_callback(self):
        self.read()
        
    def setup_append_data(self, time_array=True, autotrim=False, 
                          autotrim_limit=None):
        self.append_data = True
        self.create_dataframe(time_array)
        self.autotrim = autotrim
        if autotrim_limit:
            self.autotrim_limit = autotrim_limit
        self.auto_register_every_n_samples_event()
        self.auto_register_done_event()
    
    def autotrim_dataframe(self):
        """Trims off the oldest rows in the DataFrame to keep it smaller
        than `autotrim_limit`."""
        current_size = np.size(self.data)
        if current_size > self.autotrim_limit:
            rows, columns = np.shape(self.data)
            newrows = self.autotrim_limit//columns
            self.data = self.data.iloc[newrows:]
                               
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
        if not self.sample_clock_configured:
            self.configure_sample_clock()
        daqmx.StartTask(self.handle)

    def stop(self):
        daqmx.StopTask(self.handle)
        if self.autolog:
            self.autolog_file_object.close()
        
    def clear(self):
        daqmx.ClearTask(self.handle)
        

class SingleChannelAnalogInputVoltageTask(Task):
    def __init__(self, name, phys_chan):
        Task.__init__(self)
        channel = channels.AnalogInputVoltageChannel()
        channel.physical_channel = phys_chan
        channel.name = name
        self.add_channel(channel)

if __name__ == "__main__":
    pass
