# -*- coding: utf-8 -*-
"""
Created on Tue May 21 21:06:37 2013

@author: Pete

This program commands a National Instruments counter output device to send a
pulse after a target position (read from the ACS controller) is reached.

"""
import daqmx
import acsc
import time
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

def main():

    taskhandle = daqmx.TaskHandle()
    
    daqmx.CreateTask("", taskhandle)
    phys_chan = "Dev1/ctr0"  
    
    #Timing parameters
    rate = 200          # Pulse rate in Hz
    initialdelay = 0
    lowtime = 1/rate/2
    hightime = 1/rate/2
    
    
    daqmx.CreateCOPulseChanTime(taskhandle, phys_chan, "", daqmx.Val_Seconds, 
                                daqmx.Val_Low, initialdelay, lowtime, hightime,
                                False)
    
    # Set up communication with motion controller
    simulator = True
    
    # Parameters for plotting
    plotting = False
    plot_dynamic = True
    
    if simulator == True:
        hcomm = acsc.OpenCommDirect()
    else:
        hcomm = acsc.OpenCommEthernetTCP("10.0.0.100", 701)
    
    axis = 5
    buffno = 6
    target = 10000
    timeout = 10
    
    # Initialize arrays for storing time and position
    t = np.array(0)
    x = np.array(0)
    
    if plotting == True and plot_dynamic == True:
        plt.ioff()
        fig = plt.figure()
        ax = fig.add_subplot(111)
    #    plt.xlim(0, timeout)
    #    plt.ylim(0, target)
        line, = ax.plot([], [])
        fig.show()
    
    if hcomm == acsc.INVALID:
        print "Cannot connect to controller. Error:", acsc.GetLastError()
        
    else:
        acsc.Enable(hcomm, axis)
        rpos = acsc.GetRPosition(hcomm, axis)
        x = rpos
        t0 = time.time()
        
        if simulator == True:
            acsc.ToPoint(hcomm, 0, axis, target+50000)
        else:
            acsc.RunBuffer(hcomm, buffno, None, None)
        
        while True:
            rpos = acsc.GetRPosition(hcomm, axis)
            if rpos >= target: break
            x = np.append(x, rpos)
            t = np.append(t, time.time() - t0)
            
            if plotting == True and plot_dynamic == True:
                line.set_xdata(t)
                line.set_ydata(x)
                ax.relim()
                ax.autoscale_view()
                fig.canvas.draw()

            print "Axis is", acsc.GetAxisState(hcomm, axis)+'...'
            
            if time.time() - t0 > timeout:
                print "Motion timeout"
                print "Final axis position:", rpos
                break

            time.sleep(0.001)
            
        print "Target reached. Sending trigger pulse to", phys_chan + "..."
        
        
        daqmx.StartTask(taskhandle, fatalerror=False)
        daqmx.WaitUntilTaskDone(taskhandle, timeout=10, fatalerror=False)
    
    daqmx.ClearTask(taskhandle, fatalerror=False)
    acsc.CloseComm(hcomm)
    
    print "Triggered at", np.max(x)
    
    if plotting == True:
        if plot_dynamic == False:
            plt.plot(t, x)
    plt.show()
    
    return t, x    

if __name__ == "__main__":
    t, x = main()   