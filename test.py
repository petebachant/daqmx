# -*- coding: utf-8 -*-
"""
Created on Wed Nov 12 16:09:27 2014

@author: Pete
"""

import daqmx

if __name__ == "__main__":
#    daqmx.tests.test_task()
#    daqmx.tasks.test_task_autologging(".csv", duration=5)
    daqmx.tasks.test_task_autotrim()