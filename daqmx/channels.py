# -*- coding: utf-8 -*-
"""
Created on Wed Nov 12 15:59:12 2014

@author: Pete
"""

class Channel(object):
    """DAQmx channel object. Valid channel types are:
      * Analog input
      * Analog output
      * Global virtual
      * Digital input
      * Digital output
      * Counter input"""
    def __init__(self, channel_type):
        pass