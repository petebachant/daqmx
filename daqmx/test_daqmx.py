"""Tests for ``daqmx``."""

from __future__ import division, print_function
import daqmx
import time
import matplotlib.pyplot as plt
import numpy as np
from pxl import timeseries as ts
from pxl import fdiff
import pandas as pd
import os


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


def test_GetTrigSrcWithDevPrefix():
    th = daqmx.TaskHandle()
    daqmx.CreateTask("", th)
    daqmx.AddGlobalChansToTask(th, "drag_left")
    print(daqmx.GetTrigSrcWithDevPrefix(th, "PFI0"))


class NiDaqThread(object):
    def __init__(self, usetrigger=True):
        # Some parameters for the thread
        self.usetrigger = usetrigger

        self.collect = True

        # Create some meta data for the run
        self.metadata = {}

        # Initialize sample rate
        self.sr = 2000.0
        self.metadata["Sample rate (Hz)"] = self.sr
        self.nsamps = int(self.sr / 10)

        # Create a dict of arrays for storing data
        self.data = {
            "turbine_angle": np.array([]),
            "turbine_rpm": np.array([]),
            "torque_trans": np.array([]),
            "torque_arm": np.array([]),
            "drag_left": np.array([]),
            "drag_right": np.array([]),
            "t": np.array([]),
            "carriage_pos": np.array([]),
        }
        # Create one analog and one digital task
        # Probably should be a bridge task in there too!
        self.analogtask = daqmx.TaskHandle()
        self.carpostask = daqmx.TaskHandle()
        self.turbangtask = daqmx.TaskHandle()

        # Create tasks
        daqmx.CreateTask("", self.analogtask)
        daqmx.CreateTask("", self.carpostask)
        daqmx.CreateTask("", self.turbangtask)

        # Add channels to tasks
        self.analogchans = ["torque_trans", "torque_arm", "drag_left", "drag_right"]
        self.carposchan = "carriage_pos"
        self.turbangchan = "turbine_angle"
        daqmx.AddGlobalChansToTask(self.analogtask, self.analogchans)
        daqmx.AddGlobalChansToTask(self.carpostask, self.carposchan)
        daqmx.AddGlobalChansToTask(self.turbangtask, self.turbangchan)

        # Get channel information to add to metadata
        self.chaninfo = {}
        for channame in self.analogchans:
            self.chaninfo[channame] = {}
            scale = channame + "_scale"
            self.chaninfo[channame]["Scale name"] = scale
            self.chaninfo[channame]["Scale slope"] = daqmx.GetScaleLinSlope(scale)
            self.chaninfo[channame]["Scale y-intercept"] = daqmx.GetScaleLinYIntercept(
                scale
            )
            self.chaninfo[channame]["Scaled units"] = daqmx.GetScaleScaledUnits(scale)
            self.chaninfo[channame]["Prescaled units"] = daqmx.GetScalePreScaledUnits(
                scale
            )

        self.chaninfo[self.turbangchan] = {}
        self.chaninfo[self.turbangchan][
            "Pulses per rev"
        ] = daqmx.GetCIAngEncoderPulsesPerRev(self.turbangtask, self.turbangchan)
        self.chaninfo[self.turbangchan]["Units"] = daqmx.GetCIAngEncoderUnits(
            self.turbangtask, self.turbangchan
        )

        self.chaninfo[self.carposchan] = {}
        self.chaninfo[self.carposchan][
            "Distance per pulse"
        ] = daqmx.GetCILinEncoderDisPerPulse(self.carpostask, self.carposchan)
        self.chaninfo[self.carposchan]["Units"] = daqmx.GetCILinEncoderUnits(
            self.carpostask, self.carposchan
        )
        self.metadata["Channel info"] = self.chaninfo

        # Configure sample clock timing
        daqmx.CfgSampClkTiming(
            self.analogtask,
            "",
            self.sr,
            daqmx.Val_Rising,
            daqmx.Val_ContSamps,
            self.nsamps,
        )
        # Get source for analog sample clock
        trigname = daqmx.GetTerminalNameWithDevPrefix(self.analogtask, "ai/SampleClock")
        daqmx.CfgSampClkTiming(
            self.carpostask,
            trigname,
            self.sr,
            daqmx.Val_Rising,
            daqmx.Val_ContSamps,
            self.nsamps,
        )
        daqmx.CfgSampClkTiming(
            self.turbangtask,
            trigname,
            self.sr,
            daqmx.Val_Rising,
            daqmx.Val_ContSamps,
            self.nsamps,
        )

        # If using trigger for analog signals set source to chassis PFI0
        if self.usetrigger:
            daqmx.CfgDigEdgeStartTrig(
                self.analogtask, "/cDAQ9188-16D66BB/PFI0", daqmx.Val_Falling
            )

        # Set trigger functions for counter channels
        daqmx.SetStartTrigType(self.carpostask, daqmx.Val_DigEdge)
        daqmx.SetStartTrigType(self.turbangtask, daqmx.Val_DigEdge)
        trigsrc = daqmx.GetTrigSrcWithDevPrefix(self.analogtask, "ai/StartTrigger")
        print("Trigger source:", trigsrc)
        daqmx.SetDigEdgeStartTrigSrc(self.carpostask, trigsrc)
        daqmx.SetDigEdgeStartTrigSrc(self.turbangtask, trigsrc)
        daqmx.SetDigEdgeStartTrigEdge(self.carpostask, daqmx.Val_Rising)
        daqmx.SetDigEdgeStartTrigEdge(self.turbangtask, daqmx.Val_Rising)

    def run(self, dur):
        """Start DAQmx tasks."""

        # Acquire and throwaway samples for alignment
        # Need to set these up on a different task?
        # Callback code from PyDAQmx
        class MyList(list):
            pass

        # List where the data are stored
        data = MyList()
        id_data = daqmx.create_callbackdata_id(data)

        def EveryNCallback_py(
            taskHandle, everyNsamplesEventType, nSamples, callbackData_ptr
        ):
            """Function called every N samples"""
            callbackdata = daqmx.get_callbackdata_from_id(callbackData_ptr)
            data, npoints = daqmx.ReadAnalogF64(
                taskHandle,
                self.nsamps,
                10.0,
                daqmx.Val_GroupByChannel,
                self.nsamps,
                len(self.analogchans),
            )
            callbackdata.extend(data.tolist())
            self.data["torque_trans"] = np.append(
                self.data["torque_trans"], data[:, 0], axis=0
            )
            self.data["torque_arm"] = np.append(
                self.data["torque_arm"], data[:, 1], axis=0
            )
            self.data["drag_left"] = np.append(
                self.data["drag_left"], data[:, 2], axis=0
            )
            self.data["drag_right"] = np.append(
                self.data["drag_right"], data[:, 3], axis=0
            )
            self.data["t"] = (
                np.arange(len(self.data["torque_trans"]), dtype=float) / self.sr
            )
            carpos, cpoints = daqmx.ReadCounterF64(
                self.carpostask, self.nsamps, 10.0, self.nsamps
            )
            self.data["carriage_pos"] = np.append(self.data["carriage_pos"], carpos)
            turbang, cpoints = daqmx.ReadCounterF64(
                self.turbangtask, self.nsamps, 10.0, self.nsamps
            )
            self.data["turbine_angle"] = np.append(self.data["turbine_angle"], turbang)
            self.data["turbine_rpm"] = ts.smooth(
                fdiff.second_order_diff(self.data["turbine_angle"], self.data["t"])
                / 6.0,
                50,
            )
            return 0  # The function should return an integer

        # Convert the python callback function to a CFunction
        EveryNCallback = daqmx.EveryNSamplesEventCallbackPtr(EveryNCallback_py)
        daqmx.RegisterEveryNSamplesEvent(
            self.analogtask,
            daqmx.Val_Acquired_Into_Buffer,
            self.nsamps,
            0,
            EveryNCallback,
            id_data,
        )

        def DoneCallback_py(taskHandle, status, callbackData_ptr):
            print("Status", status.value)
            return 0

        DoneCallback = daqmx.DoneEventCallbackPtr(DoneCallback_py)
        daqmx.RegisterDoneEvent(self.analogtask, 0, DoneCallback, None)

        # Start the tasks
        daqmx.StartTask(self.carpostask)
        daqmx.StartTask(self.turbangtask)
        daqmx.StartTask(self.analogtask)

        time.sleep(dur)
        self.clear()

    def stopdaq(self):
        daqmx.StopTask(self.analogtask)
        daqmx.StopTask(self.carpostask)
        daqmx.StopTask(self.turbangtask)

    def clear(self):
        self.stopdaq()
        daqmx.ClearTask(self.analogtask)
        daqmx.ClearTask(self.carpostask)
        daqmx.ClearTask(self.turbangtask)
        self.collect = False


def test_ni_daq_thread(dur=1):
    t = NiDaqThread(usetrigger=False)
    t.run(dur)
    plt.plot(t.data["t"], t.data["drag_left"])


def test_task(duration=3):
    import time
    import matplotlib.pyplot as plt

    task = daqmx.tasks.Task()
    c = daqmx.channels.AnalogInputVoltageChannel()
    c.physical_channel = "Dev1/ai0"
    c.name = "analog input 0"
    task.add_channel(c)
    c2 = daqmx.channels.AnalogInputVoltageChannel()
    c2.physical_channel = "Dev1/ai1"
    c2.name = "analog input 1"
    task.add_channel(c2)
    task.setup_append_data()
    task.start()
    time.sleep(duration)
    task.stop()
    task.clear()
    plt.plot(task.data["time"], task.data[c.name])
    plt.plot(task.data["time"], task.data[c2.name])


def test_task_autologging(filetype=".csv", duration=3):
    import time
    import matplotlib.pyplot as plt
    from pxl import timeseries

    print("Testing autologging to", filetype)
    task = daqmx.tasks.Task()
    c = daqmx.channels.AnalogInputVoltageChannel()
    c.physical_channel = "Dev1/ai0"
    c.name = "analog input 0"
    task.add_channel(c)
    c2 = daqmx.channels.AnalogInputVoltageChannel()
    c2.physical_channel = "Dev1/ai1"
    c2.name = "analog input 1"
    task.add_channel(c2)
    task.setup_autologging("test" + filetype, newfile=True)
    task.start()
    time.sleep(duration)
    task.stop()
    task.clear()
    if filetype == ".csv":
        data = pd.read_csv("test" + filetype)
    else:
        data = timeseries.loadhdf("test" + filetype)
    plt.plot(data["time"], data["analog input 0"])
    plt.plot(data["time"], data["analog input 1"])
    print("Deleting test CSV")
    os.remove("test.csv")


def test_task_autotrim(duration=5):
    print("Testing task autotrim functionality")
    import time
    import matplotlib.pyplot as plt

    task = daqmx.tasks.Task()
    c = daqmx.channels.AnalogInputVoltageChannel()
    c.physical_channel = "Dev1/ai0"
    c.name = "analog input 0"
    task.add_channel(c)
    c2 = daqmx.channels.AnalogInputVoltageChannel()
    c2.physical_channel = "Dev1/ai1"
    c2.name = "analog input 1"
    task.add_channel(c2)
    task.setup_append_data(autotrim=True, autotrim_limit=100)
    task.start()
    time.sleep(duration)
    task.stop()
    task.clear()
    plt.plot(task.data["time"], task.data[c.name])
    plt.plot(task.data["time"], task.data[c2.name])
    assert len(task.data) < task.autotrim_limit
    print("PASS")
