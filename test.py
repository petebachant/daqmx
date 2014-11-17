# -*- coding: utf-8 -*-
"""
Created on Wed Nov 12 16:09:27 2014

@author: Pete
"""
from __future__ import division, print_function
import daqmx
import time
import matplotlib.pyplot as plt

def test_single_channel_analog_input_task(duration=3):
    task = daqmx.tasks.SingleChannelAnalogInputVoltageTask("ai0", "Dev1/ai0")
    task.sample_rate = 1000
    task.setup_append_data()
    task.start()
    time.sleep(duration)
    task.stop()
    task.clear()
    plt.plot(task.data["time"], task.data["ai0"])
    
def test_analog_input_bridge(duration=3):
    c = daqmx.channels.AnalogInputBridgeChannel()
    c.physical_channel = "cDAQ1Mod2/ai0"
    c.name = "bridge"
    task = daqmx.tasks.Task()
    task.add_channel(c)
    task.setup_append_data()
    task.start()
    time.sleep(duration)
    task.stop()
    task.clear()
    plt.plot(task.data["time"], task.data["bridge"])
    
def test_global_virtual_channel():
    th = daqmx.TaskHandle()
    daqmx.CreateTask("", th)
    daqmx.AddGlobalChansToTask(th, "drag_left")
    daqmx.AddGlobalChansToTask(th, ["drag_right", "torque_trans"])
    daqmx.ClearTask(th)
    
def test_get_sys_global_channels():
    print(daqmx.GetSysGlobalChans())
    
def test_get_dev_ai_phys_channels():
    print(daqmx.GetDevAIPhysicalChans("Dev1"))
    
def test_GetTerminalNameWithDevPrefix():
    th = daqmx.TaskHandle()
    daqmx.CreateTask("", th)
    daqmx.AddGlobalChansToTask(th, "drag_left")
    print(daqmx.GetTerminalNameWithDevPrefix(th, "PFI0"))
    

if __name__ == "__main__":
#    daqmx.tests.test_task()
#    daqmx.tasks.test_task_autologging(".csv", duration=5)
#    daqmx.tasks.test_task_autotrim()
#    test_single_channel_analog_input_task()
    test_analog_input_bridge()
#    test_global_virtual_channel()
#    test_get_sys_global_channels()
#    test_get_dev_ai_phys_channels()
#    test_GetTerminalNameWithDevPrefix()