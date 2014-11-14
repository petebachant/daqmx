# -*- coding: utf-8 -*-
"""
Created on Wed Nov 12 16:09:27 2014

@author: Pete
"""

import daqmx

def test_single_channel_analog_input_task(duration=3):
    import time
    import matplotlib.pyplot as plt
    task = daqmx.tasks.SingleChannelAnalogInputVoltageTask("ai0", "Dev1/ai0")
    task.sample_rate = 1000
    task.setup_append_data()
    task.start()
    time.sleep(duration)
    task.stop()
    task.clear()
    plt.plot(task.data["time"], task.data["ai0"])

if __name__ == "__main__":
#    daqmx.tests.test_task()
#    daqmx.tasks.test_task_autologging(".csv", duration=5)
#    daqmx.tasks.test_task_autotrim()
    test_single_channel_analog_input_task()