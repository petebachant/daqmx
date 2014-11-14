# -*- coding: utf-8 -*-
"""
Created on Wed Nov 12 15:59:12 2014

@author: Pete
"""

class Channel(object):
    """DAQmx channel object. Valid channel types are:
      * analog input voltage
      * analog output voltage
      * digital input
      * digital output
      * counter input"""
    def __init__(self):
        self.channel_type = ""
        self.name = ""
        self.physical_channel = ""
        self.terminal_config = "differential"
        self.minval = -10.0
        self.maxval = 10.0
        self.units = "volts"
        self.custom_scale_name = None
        self.bridge_config = None
        self.voltage_exc_source = None
        self.voltage_exc_value = None


class AnalogInputVoltageChannel(Channel):
    """Analog input voltage channel object."""
    def __init__(self):
        Channel.__init__(self)
        self.channel_type = "analog input voltage"

        
class AnalogInputBridgeChannel(Channel):
    def __init__(self):
        Channel.__init__(self)
        self.channel_type = "analog input bridge"
        self.units = "volts per volt"
        self.bridge_config = "full bridge"
        self.voltage_exc_source = "internal"
        self.voltage_exc_value = 10.0
        self.nominal_bridge_resistance = 350.0
        self.minval = -0.025
        self.maxval = 0.025


class GlobalVirtualChannel(Channel):
    """Global Virtual Channel object."""
    def __init__(self):
        Channel.__init__(self)
        self.is_global_virtual = True
        
        
def test_channel():
    c = Channel()
    print(c.name)
    
if __name__ == "__main__":
    test_channel()