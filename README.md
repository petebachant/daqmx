daqmx
=====
A [work-in-progress] wrapper to the National Instruments DAQmx driver. It depends on PyDAQmx for callbacks, and all of the functions may be available through PyDAQmx, but the syntax is slightly different. 

### Motivation
PyDAQmx works well, but its members don't show up in Spyder's autocompletion. Also, PyDAQmx has some syntax that is difficult to work with. 

### Status

As of yet, only the functions and constants that I have needed are wrapped, so things are a bit incomplete.

Installation
------------
Inside the cloned directory run
```
python setup.py install
```
