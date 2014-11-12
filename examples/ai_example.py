# -*- coding: utf-8 -*-
"""
Created on Tue May 21 21:06:37 2013

@author: Pete

This program aquires finite analog samples.

"""
from __future__ import division, print_function
import daqmx
import time
import numpy as np
import matplotlib
#matplotlib.use("TkAgg")
import matplotlib.pyplot as plt


def main():

    # Task parameters
    taskhandle = daqmx.TaskHandle()
    daqmx.CreateTask("", taskhandle)
    phys_chan = b"Dev1/ai0"
    nchan = 1
    sr = 100.0
    dt = 1/sr
    totaltime = 3
    nloops = int(sr*totaltime/10)
    
    # Analog read parameters
    samps_per_chan = 10
    timeout = 10
    fillmode = daqmx.Val_GroupByChannel
    array_size_samps = 1000
    
    
    daqmx.CreateAIVoltageChan(taskhandle, phys_chan, "", daqmx.Val_Diff,
                              -10.0, 10.0, daqmx.Val_Volts, None)
                              
                              
    daqmx.CfgSampClkTiming(taskhandle, "", sr, daqmx.Val_Rising, 
                           daqmx.Val_ContSamps, 1000)
    
    
    # Parameters for plotting
    plotting = True
    plot_dynamic = True

    if plotting == True and plot_dynamic == True:
        plt.ioff()
        fig = plt.figure()
        ax = fig.add_subplot(111)
        line, = ax.plot([],)
        fig.show()
    
    
    daqmx.StartTask(taskhandle, fatalerror=False)
    

    v = np.array([])
    
    for n in range(nloops):
        data, spc = daqmx.ReadAnalogF64(taskhandle, samps_per_chan, timeout, 
                                        fillmode, array_size_samps, nchan)
        v = np.append(v, data[:,0]) 
        time.sleep(0.001)
        t = np.float64(range(len(v)))*dt 

        if plotting == True and plot_dynamic == True:
            line.set_xdata(t)
            line.set_ydata(v)
            ax.relim()
            ax.autoscale_view()
            fig.canvas.draw()                         
                                    

    daqmx.ClearTask(taskhandle)  
    print("Task complete")    

    
    if plotting == True:
        if plot_dynamic == False:
            plt.plot(t, v)
    plt.show()
    
    return t, data  

if __name__ == "__main__":
    v, data = main()   