#!/usr/bin/env python
"""
Adapted from 
https://github.com/ap--/python-live-plotting/blob/master/plot_pyqtgraph.py
"""
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import daqmx

class DynamicPlotter():
    def __init__(self, size=(600,350)):
        # PyQtGraph setup
        self.app = QtGui.QApplication([])
        self.plt = pg.plot(title='Dynamic Plotting with PyQtGraph')
        self.plt.resize(*size)
        self.plt.showGrid(x=True, y=True)
        self.plt.setLabel('left', 'Volts', 'V')
        self.plt.setLabel('bottom', 'Time', 's')
        self.setup_ni()
        self.curve = self.plt.plot([], [], pen=(255,0,0))
        # QTimer setup
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateplot)
        self.timer.start(80)
        
    def setup_ni(self):
        self.task = daqmx.tasks.Task()
        self.channel = daqmx.channels.AnalogInputVoltageChannel()
        self.channel.physical_channel = "Dev1/ai0"
        self.channel.name = "volts"
        self.task.add_channel(self.channel)
        self.task.sample_rate = 100
        self.task.setup_append_data(autotrim=True, autotrim_limit=6000)

    def updateplot(self):
        self.curve.setData(self.task.data["time"], self.task.data["volts"])
        self.app.processEvents()

    def run(self):
        self.task.start()
        self.app.exec_()
        
    def closeEvent(self):
        self.task.stop()
        self.task.clear()

if __name__ == '__main__':
    m = DynamicPlotter()
    m.run()