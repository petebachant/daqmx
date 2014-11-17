# -*- coding: utf-8 -*-
"""
This program is a wrapper to the NIDAQmx C library using ctypes.
It depends on PyDAQmx for doing callbacks.

All functions have the same camel case naming scheme.

@author: Pete Bachant

"""
from __future__ import print_function, division
from PyDAQmx.DAQmxTypes import DAQmxEveryNSamplesEventCallbackPtr as EveryNSamplesEventCallbackPtr
from PyDAQmx.DAQmxTypes import DAQmxDoneEventCallbackPtr as DoneEventCallbackPtr
from PyDAQmx.DAQmxTypes import DAQmxSignalEventCallbackPtr as SignalEventCallbackPtr
from PyDAQmx.DAQmxCallBack import *
import ctypes
from ctypes import byref
import numpy as np

dmx = ctypes.windll.LoadLibrary("nicaiu.dll")

int32 = ctypes.c_long
uInt32 = ctypes.c_ulong
uInt64 = ctypes.c_ulonglong
double = ctypes.c_double
char = ctypes.c_char
cstr = ctypes.c_char_p
p = ctypes.pointer
TaskHandle = ctypes.c_void_p
cfloat = ctypes.c_float


def CreateTask(taskname, taskhandle):
    """Creates a DAQmx task."""
    ErrorHandling(dmx.DAQmxCreateTask(taskname, byref(taskhandle)))


def CreateCOPulseChanTime(taskhandle, phys_chan, chan_name, units,
        idlestate, initialdelay, lowtime, hightime, fatalerror=True):
    """Creates a counter output channel based on pulse time."""
    initialdelay = double(initialdelay)
    lowtime = double(lowtime)
    hightime = double(hightime)
    rv = dmx.DAQmxCreateCOPulseChanTime(taskhandle, phys_chan, chan_name,
        units, idlestate, initialdelay, lowtime, hightime)
    ErrorHandling(rv, fatalerror)


def CfgImplicitTiming(taskhandle, samplemode, sampsPerChanToAcquire, 
                      fatalerror=False):
    rv = dmx.DAQmxCfgImplicitTiming(taskhandle, samplemode, 
                                    uInt64(sampsPerChanToAcquire))
    ErrorHandling(rv, fatalerror)
    

def CfgDigEdgeStartTrig(taskHandle, triggerSource, triggerEdge):
    """Configures the task to start acquiring or generating samples on a 
    rising or falling edge of a digital signal."""
    triggerSource = input_string(triggerSource)
    dmx.DAQmxCfgDigEdgeStartTrig(taskHandle, triggerSource, int32(triggerEdge))


def AddGlobalChansToTask(taskhandle, channelnames, fatalerror=True):
    """
DAQmxAddGlobalChansToTask
=========================
int32 DAQmxAddGlobalChansToTask (TaskHandle taskHandle, const char channelNames[]);

Purpose
-------
Adds global virtual channels from MAX to the given task.

Parameters
----------
taskhandle: The task handle to which to add the channels from MAX. \n
channelnames: List containing channel names
    """
    if type(channelnames) == list:
        channelnames = ", ".join(channelnames)
    channelnames = input_string(channelnames)
    rv = dmx.DAQmxAddGlobalChansToTask(taskhandle, channelnames)
    ErrorHandling(rv, fatalerror)
    

def CreateAIVoltageChan(taskhandle, phys_chan, name_to_assign, terminalconfig,
        minval, maxval, units, custom_scale_name=None, fatalerror=True):
    """Creates an analog voltage input channel"""
    if type(phys_chan) == str:
        phys_chan = phys_chan.encode()
    rv = dmx.DAQmxCreateAIVoltageChan(taskhandle, phys_chan, name_to_assign, 
        int32(terminalconfig), double(minval), double(maxval), int32(units), 
        custom_scale_name)
    ErrorHandling(rv, fatalerror)


def CreateAIBridgeChan(taskhandle, phys_chan, name_to_assign, minval, 
        maxval, units, bridge_config, voltage_exc_source, voltage_exc_val, 
        nominal_bridge_resistance, custom_scale_name=None):
    """Creates an analog input bridge channel."""
    if type(phys_chan) == str:
        phys_chan = phys_chan.encode()
    rv = dmx.DAQmxCreateAIBridgeChan(taskhandle, phys_chan, name_to_assign, 
            double(minval), double(maxval), int32(units), int32(bridge_config), 
            int32(voltage_exc_source), double(voltage_exc_val), 
            double(nominal_bridge_resistance), custom_scale_name);
    ErrorHandling(rv)
    

def CreateAOVoltageChan(taskHandle, physicalChannel, nameToAssignToChannel, 
        minVal, maxVal, units, customScaleName, fatalerror=True):
    """"Creates an analog voltage output channel."""
    if type(physicalChannel) == str:
        physicalChannel = physicalChannel.encode()
    rv = dmx.DAQmxCreateAOVoltageChan(taskHandle, physicalChannel, 
        nameToAssignToChannel, double(minVal), double(maxVal), int32(units), 
        customScaleName)
    ErrorHandling(rv, fatalerror)


def CreateDIChan(taskhandle, lines, nameToAssignToLines, linegrouping, 
                 fatalerror=True):
    """Creates a digital input channel."""
    rv = dmx.DAQmxCreateDIChan(taskhandle, lines, nameToAssignToLines,
                               int32(linegrouping))
    ErrorHandling(rv, fatalerror)


def GetDevAIPhysicalChans(device, buffersize=512, fatalerror=False):
    """Get device analog input channels."""
    channels = ctypes.create_string_buffer(buffersize)
    if type(device) == str:
        device = device.encode()
    rv = dmx.DAQmxGetDevAIPhysicalChans(device, byref(channels), 
                                        uInt32(buffersize))
    ErrorHandling(rv, fatalerror)
    chans = channels.value.decode()
    return chans.split(", ")
    
    
def GetSysGlobalChans(buffersize=512):
    """Returns a list of system global channels."""
    channels = ctypes.create_string_buffer(buffersize)
    rv = dmx.DAQmxGetSysGlobalChans(byref(channels), uInt32(buffersize))
    ErrorHandling(rv, fatalerror=False)
    channels = output_string(channels.value)
    return channels.split(", ")
    

def StartTask(taskhandle, fatalerror=True):
    """Starts a DAQmx task."""
    ErrorHandling(dmx.DAQmxStartTask(taskhandle), fatalerror)
        

def CfgSampClkTiming(taskhandle, source, rate, active_edge, sample_mode,
                     samps_per_chan, fatalerror=True):
    """Configures sample clock timing."""
    if type(source) == str:
        source = source.encode()
    rv = dmx.DAQmxCfgSampClkTiming(taskhandle, source, double(rate), 
            int32(active_edge), int32(sample_mode), uInt64(samps_per_chan))
    ErrorHandling(rv, fatalerror)

        
def ReadAnalogF64(taskhandle, samps_per_chan, timeout, fillmode, 
                  array_size_samps, nchan, fatalerror=True):
    """Reads analog data."""                  
    read_array = np.zeros((samps_per_chan*nchan), dtype=np.float64)
    samps_pchan_read = int32()
    rv = dmx.DAQmxReadAnalogF64(taskhandle, uInt32(samps_per_chan), 
            double(timeout), fillmode, read_array.ctypes.data,
            uInt32(int(array_size_samps*nchan)), byref(samps_pchan_read), None)                          
    ErrorHandling(rv, fatalerror)
    # Split up read array into a column per channel
    array2d = np.zeros((samps_per_chan, nchan))
    for n in range(nchan):
        array2d[:,n] = read_array[n*samps_per_chan:(n+1)*samps_per_chan]
    return array2d, samps_pchan_read.value


def ReadCounterF64(taskHandle, numSampsPerChan, timeout, arraySizeInSamps):
    """Read counter data in as float64."""
    sampsPerChanRead = int32()
    readArray = np.zeros(numSampsPerChan)
    dmx.DAQmxReadCounterF64(taskHandle, numSampsPerChan, double(timeout), 
                            readArray.ctypes.data, 
                            arraySizeInSamps, byref(sampsPerChanRead), None)
                            
    return readArray, sampsPerChanRead.value


def WriteAnalogF64(taskHandle, numSampsPerChan, autoStart, timeout, 
                   dataLayout, writeArray, fatalerror=True):
    """Writes analog voltage. Returns samples written per channel."""
    sampsPerChanWritten = int32()
    rv = dmx.DAQmxWriteAnalogF64(taskHandle, int32(numSampsPerChan), 
            autoStart, double(timeout), dataLayout, writeArray.ctypes.data, 
            byref(sampsPerChanWritten), None)
    ErrorHandling(rv, fatalerror)
    return sampsPerChanWritten.value


def ReadDigitalU32(taskHandle, sampsPerChan, timeout, fillMode, 
                   arraySizeInSamps, nchan, fatalerror=True):
    """Reads digital data. Returns an array of samples and the number of 
    samples read per channel."""
    sampsPerChanRead = int32()
    readArray = np.zeros((sampsPerChan, nchan), dtype=np.uint32)
    rv = dmx.DAQmxReadDigitalU32(taskHandle, int32(sampsPerChan), 
            double(timeout), fillMode, readArray.ctypes.data, 
            uInt32(arraySizeInSamps), byref(sampsPerChanRead), None)
    ErrorHandling(rv, fatalerror)
    return readArray, sampsPerChanRead.value                                 


def WaitUntilTaskDone(taskhandle, timeout, fatalerror=True):
    rv = dmx.DAQmxWaitUntilTaskDone(taskhandle, double(timeout))
    ErrorHandling(rv, fatalerror)    


def StopTask(taskhandle, fatalerror=True):
    """Stops a DAQmx task."""
    ErrorHandling(dmx.DAQmxStopTask(taskhandle), fatalerror)
        

def ClearTask(taskhandle, fatalerror=True):
    """Clears a DAQmx task."""
    rv = dmx.DAQmxClearTask(taskhandle)
    ErrorHandling(rv, fatalerror)
    
    
def GetNthTaskDevice(taskhandle, index, buffersize):
    device = ctypes.create_string_buffer(buffersize)
    dmx.DAQmxGetNthTaskDevice(taskhandle, uInt32(index), byref(device), 
                              int32(buffersize))
    dev = device.value
    return output_string(dev)
    
    
def GetDevProductCategory(device):
    prodcat = int32()
    dmx.DAQmxGetDevProductCategory(device, byref(prodcat))
    return prodcat.value
    

def GetTaskNumDevices(taskhandle):
    numdevices = uInt32()
    dmx.DAQmxGetTaskNumDevices(taskhandle, byref(numdevices))
    return numdevices.value


def GetTerminalNameWithDevPrefix(taskhandle, terminalname):
    """Gets terminal name with device prefix.
       Returns trigger name."""
    ndev = GetTaskNumDevices(taskhandle)
    for i in range(1, ndev+1):
         device = GetNthTaskDevice(taskhandle, i, 256)
         pcat = GetDevProductCategory(device)
         if pcat != Val_CSeriesModule and pcat != Val_SCXIModule:
             triggername = "/" + device + "/" + terminalname
             break
    return triggername
    

def GetTrigSrcWithDevPrefix(taskhandle, terminalname):
    """Gets terminal name with device prefix and returns trigger name."""
    ndev = GetTaskNumDevices(taskhandle)
    for i in range(1, ndev+1):
         device = GetNthTaskDevice(taskhandle, i, 256)
         pcat = GetDevProductCategory(device)
         if pcat != Val_CSeriesModule and pcat != Val_SCXIModule:
             triggername = "/" + device + "/" + terminalname
             break
    return triggername    


def SetStartTrigType(taskhandle, trigtype):
    """Sets start trigger type."""
    dmx.DAQmxSetStartTrigType(taskhandle, trigtype)


def SetDigEdgeStartTrigSrc(taskhandle, trigsrc):
    """Sets digital edge start trigger source."""
    dmx.DAQmxSetDigEdgeStartTrigSrc(taskhandle, input_string(trigsrc))


def SetDigEdgeStartTrigEdge(taskhandle, trigedge):
    """Sets digital edge start trigger edge."""
    dmx.DAQmxSetDigEdgeStartTrigEdge(taskhandle, input_string(trigedge))


def GetScaleAttribute(scalename, attribute):
    """Gets a scale attribute. Need to get constants for attributes"""
    value = double()
    dmx.DAQmxGetScaleAttribute(input_string(scalename), attribute, byref(value))
    return value


def GetScaleLinSlope(scalename):
    """Returns scale linear slope value."""
    linslope = double()
    dmx.DAQmxGetScaleLinSlope(input_string(scalename), byref(linslope))
    return linslope.value
    
    
def GetScaleLinYIntercept(scalename):
    """Returns scale linear y-intercept"""
    yint = double()
    dmx.DAQmxGetScaleLinYIntercept(input_string(scalename), byref(yint))
    return yint.value
    
    
def GetScaleScaledUnits(scalename, buffersize=512):
    scaledunits = ctypes.create_string_buffer(buffersize)
    dmx.DAQmxGetScaleScaledUnits(input_string(scalename), byref(scaledunits), buffersize)
    return output_string(scaledunits.value)
    

def GetScalePreScaledUnits(scalename):
    unitint = uInt32()
    dmx.DAQmxGetScalePreScaledUnits(input_string(scalename), byref(unitint))
    unitint = unitint.value
    if unitint in units:
        return units[unitint]
    else: 
        return None

    
def GetCIAngEncoderUnits(taskhandle, channel):
    data = int32()
    dmx.DAQmxGetCIAngEncoderUnits(taskhandle, channel, byref(data))
    if data.value in units:
        return units[data.value]
    else: return data.value


def GetCIAngEncoderPulsesPerRev(taskhandle, channel):
    data = uInt32()
    dmx.DAQmxGetCIAngEncoderPulsesPerRev(taskhandle, channel, byref(data))
    return int(data.value)

    
def GetCILinEncoderDisPerPulse(taskhandle, channel):
    """Get linear encoder distance per pulse."""
    data = double()
    dmx.DAQmxGetCILinEncoderDistPerPulse(taskhandle, channel, byref(data))
    return data.value
    

def GetCILinEncoderUnits(taskhandle, channel):
    """Get linear encoder units."""
    data = int32()
    dmx.DAQmxGetCILinEncoderUnits(taskhandle, channel, byref(data))
    if data.value in units:
        return units[data.value]
    else: return data.value
    

def GetAICustomScaleName(taskhandle, channel, buffersize=512):
    """Gets a custom scale name from an analog input task."""
    scalename = ctypes.create_string_buffer(buffersize)
    channel = input_string(channel)
    dmx.DAQmxGetAICustomScaleName(taskhandle, channel, byref(scalename), 
                                  buffersize)
    return output_string(scalename.value)


def GetCICustomScaleName(taskhandle, channel):
    scalename = ctypes.create_string_buffer(512)
    channel = input_string(channel)
    dmx.DAQmxGetCICustomScaleName(taskhandle, channel, byref(scalename), 512)
    return output_string(scalename.value)


def GetChanAttribute(taskhandle, channel, attribute):
    """Gets a channel attribute."""
    value = char()
    channel = input_string(channel)
    dmx.DAQmxGetChanAttribute(taskhandle, channel, attribute, byref(value))
    return value.value
    

def GetChanType(taskhandle, channel):
    data = int32()
    channel = input_string(channel)
    dmx.DAQmxGetChanType(taskhandle, channel, byref(data))
    return data.value    
    

def GetTaskChannels(taskhandle):
    """Returns a list of channels associated with a task."""
    channels = ctypes.create_string_buffer(512)    
    dmx.DAQmxGetTaskChannels(taskhandle, byref(channels), 512)
    channels = output_string(channels.value)
    return channels.split(", ")


def GetErrorString(errorcode, buffersize=512):
    errorstring = ctypes.create_string_buffer(buffersize)
    dmx.DAQmxGetErrorString(int32(errorcode), byref(errorstring), 
                            uInt32(buffersize));
    return errorstring.value.decode()
    
    
def RegisterEveryNSamplesEvent(taskHandle, everyNsamplesEventType, nSamples, 
                               options, callbackFunction, callbackData):
    rv = dmx.DAQmxRegisterEveryNSamplesEvent(taskHandle, 
            int32(everyNsamplesEventType), uInt32(nSamples), uInt32(options),
            callbackFunction, callbackData)
    ErrorHandling(rv)
    
    
def RegisterDoneEvent(taskHandle, options, callbackFunction, callbackData):
    """Registers a done event."""
    rv = dmx.DAQmxRegisterDoneEvent(taskHandle, uInt32(options), 
                                    callbackFunction, callbackData)
    ErrorHandling(rv)
    
    
def SetWriteRegenMode(taskHandle, data):
    ErrorHandling(dmx.DAQmxSetWriteRegenMode(taskHandle, int32(data)))
    

def GetWriteSpaceAvail(taskHandle):
    writeSpaceAvail = uInt32()
    dmx.DAQmxGetWriteSpaceAvail(taskHandle, byref(writeSpaceAvail))
    return writeSpaceAvail.value
                                     

def ErrorHandling(returned_value, fatalerror=True):
    rv = returned_value
    if rv != 0:
        estring = GetErrorString(rv)
        if fatalerror == True:
            raise RuntimeError(estring)
        else: print(estring)
    else: return
    

def input_string(string):
    if type(string) == str:
        return string.encode()
    else:
        return string
        
        
def output_string(string):
    if type(string) == bytes:
        return string.decode()
    else:
        return string


# Values for DAQmx Contants
Val_SampClkPeriods = 10286      
Val_Seconds = 10364
Val_Ticks = 10304
Val_FiniteSamps = 10178
Val_ContSamps = 10123
Val_Cfg_Default  = -1
Val_High = 10192
Val_Low = 10214
Val_Volts = 10348
Val_Rising = 10280
Val_Falling = 10171
Val_GroupByChannel = 0
Val_Diff = 10106
Val_ChanForAllLines = 1
Val_CSeriesModule = 14659
Val_SCXIModule = 14660
Val_Acquired_Into_Buffer = 1
Val_Transferred_From_Buffer = 2
Val_AllowRegen = 10097
Val_DoNotAllowRegen = 10158
Val_Meters = 10219
Val_Inches = 10379
Val_FromCustomScale = 10065
Val_Degrees = 10146
Val_Radians = 10273
Val_Ticks = 10304
Val_VoltsPerVolt = 15896
Val_mVoltsPerVolt = 15897
Val_FullBridge = 10182
Val_HalfBridge = 10187
Val_QuarterBridge = 10270
Val_Internal = 10200
Val_External = 10167

# Channel attribute constants
AI_Max = 0x17DD # Specifies the maximum value you expect to measure. This value is in the units you specify with a units property. When you query this property, it returns the coerced maximum value that the device can measure with the current settings.
AI_Min = 0x17DE # Specifies the minimum value you expect to measure. This value is in the units you specify with a units property.  When you query this property, it returns the coerced minimum value that the device can measure with the current settings.
CustomScaleName = 0x17E0

# Trigger constants
Val_DigEdge = 10150


# Dict for units
units = {Val_Seconds : "s",
         Val_Meters : "m",
         Val_Degrees : "Degrees",
         Val_VoltsPerVolt : "V/V",
         Val_mVoltsPerVolt : "mV/V",
         Val_Volts : "V"}
         
parameters = {"rising" : Val_Rising,
              "falling" : Val_Falling,
              "continuous samples" : Val_ContSamps,
              "differential" : Val_Diff,
              "volts" : Val_Volts,
              "V" : Val_Volts,
              "from custom scale" : Val_FromCustomScale,
              "group by channel" : Val_GroupByChannel,
              "V/V" : Val_VoltsPerVolt,
              "volts per volt" : Val_VoltsPerVolt,
              "mV/V" : Val_mVoltsPerVolt,
              "millivolts per volt" : Val_mVoltsPerVolt,
              "full bridge" : Val_FullBridge,
              "half bridge" : Val_HalfBridge,
              "quarter bridge" : Val_QuarterBridge,
              "internal" : Val_Internal,
              "external" : Val_External}

    
if __name__ == "__main__":
    chan = "drag_left"
    th = TaskHandle()
    CreateTask("", th)
    AddGlobalChansToTask(th, chan)
    print(GetAICustomScaleName(th, chan))
    print(GetScaleLinSlope("DragLScale"))
