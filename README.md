daqmx
=====

A [work-in-progress] wrapper to the National Instruments DAQmx driver. It
depends on PyDAQmx for callbacks, and all of the functions may be available
through PyDAQmx, but the syntax is slightly different to allow for more
"Pythonic" programming.

## Motivation

PyDAQmx works well, but its members don't show up in Spyder's autocompletion.
Also, PyDAQmx uses a lot of mixed case names (including its package name),
which can be cumbersome to program with. The goal of this project is to make
syntax as clear as possible for rapid application development.

## Status

As of yet, only the functions and constants that I have needed are wrapped, so
things are a bit incomplete. Use with the knowledge that things are not
complete, and feel free to submit pull requests. 

## Installation

Inside the cloned directory run
```
python setup.py install
```

## Usage example

```
import time
import daqmx
import matplotlib.pyplot as plt

# Create a task object
task = daqmx.tasks.Task()

# Create a channel object
channel = daqmx.channels.AnalogInputVoltageChannel()
channel.physical_channel = "Dev1/ai0"
channel.name = "analog input 0"

# Add the channel to the task and activate option to append data in memory
task.add_channel(channel)
task.setup_append_data()

# Run the task for 2 seconds and stop
task.start()
time.sleep(2)
task.stop()
task.clear()

# Plot the resulting data
plt.plot(task.data["time"], task.data["analog input 0"])
plt.show()

```

