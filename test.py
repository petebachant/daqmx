# -*- coding: utf-8 -*-
"""
Created on Wed Nov 12 16:09:27 2014

@author: Pete
"""
from __future__ import division, print_function
import daqmx
from daqmx.tests import *
    
def test_all():
    test_task()
    test_task_autologging(".csv", duration=1)
    test_task_autotrim()
    test_single_channel_analog_input_task()
    test_analog_input_bridge()
    test_global_virtual_channel()
    test_get_sys_global_channels()
    test_get_dev_ai_phys_channels()
    test_GetTerminalNameWithDevPrefix()
    test_GetTrigSrcWithDevPrefix()
    test_ni_daq_thread()

if __name__ == "__main__":
#    test_task()
#    test_task_autologging(".csv", duration=1)
    test_task_autotrim()
#    test_single_channel_analog_input_task()
#    test_analog_input_bridge()
#    test_global_virtual_channel()
#    test_get_sys_global_channels()
#    test_get_dev_ai_phys_channels()
#    test_GetTerminalNameWithDevPrefix()
#    test_GetTrigSrcWithDevPrefix()
#    test_ni_daq_thread(dur=10)
#    test_all()