# -*- coding: utf-8 -*-
"""
Created on May 24 2013

@author: Pete Bachant

This program commands a National Instruments counter output device to send a
pulse 

"""

import daqmx

def main():

    # Initializing task
    taskhandle = daqmx.TaskHandle()
    daqmx.CreateTask("", taskhandle)
    phys_chan = "Dev1/ctr0"  
    
    #Timing parameters
    rate = 200.0
    initialdelay = 0
    lowtime = 1/rate/2
    hightime = 1/rate/2
    
    
    daqmx.CreateCOPulseChanTime(taskhandle, phys_chan, "", daqmx.Val_Seconds, 
                                daqmx.Val_Low, initialdelay, lowtime, hightime,
                                False)

            
    print "Sending trigger pulse to", phys_chan + "..."
    daqmx.StartTask(taskhandle, fatalerror=True)
    print "Success!"    
    
    daqmx.WaitUntilTaskDone(taskhandle, timeout=10, fatalerror=False)
    daqmx.ClearTask(taskhandle, fatalerror=False)


if __name__ == "__main__":
    main()   