# -*- coding: utf-8 -*-
"""
Created on Wed Nov 12 15:59:12 2014

@author: Pete
"""

class Channel(object):
    """DAQmx channel object. Valid channel types are:
      * analog input
      * analog output
      * global virtual
      * digital input
      * digital output
      * counter input"""
    def __init__(self):
        self.channel_type = ""
        self.name = ""
        self.physical_channel = ""
        self.is_global_virtual = False
        self.terminal_config = "differential"
        self.minval = -10.0
        self.maxval = 10.0
        self.units = "volts"
        self.custom_scale_name = None


class AnalogInputChannel(Channel):
    """Analog input channel object."""
    def __init__(self):
        Channel.__init__(self)
        self.channel_type = "analog input"
        
        
def test_channel():
    c = Channel()
    print(c.name)
    
if __name__ == "__main__":
    test_channel()