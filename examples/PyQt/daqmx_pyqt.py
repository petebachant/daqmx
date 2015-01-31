# -*- coding: utf-8 -*-
"""
Created on Wed May 29 18:17:57 2013

@author: Pete
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtGui
import PyQt4.Qwt5 as Qwt
from mainwindow import *
import sys
import time
import daqmx
import numpy as np
import wavegen


class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Setup a timer and connect appropriate slot
        self.timer = QTimer()
        self.timer.timeout.connect(self.on_timer)
        
        # Start a thread for DAQ
        self.daqthread = self.WorkThread("Dev1/ai0")
        
        # Get available physical channels
        self.chanlist = daqmx.GetDevAIPhysicalChans("Dev1", 200)
        self.ui.combo_box.addItems(self.chanlist)
        self.globchans = daqmx.GetSysGlobalChans(200)
        
        # Connect signals to appropriate slots
        self.connect_sig_slots()
        
        # Add some labels to the status bar
        self.clabel = QLabel()
        self.clabel.setText("Not connected ")
        self.ui.statusbar.addWidget(self.clabel)
        
        # Create plot
        self.plot = self.ui.figure
        self.plot.setCanvasBackground(Qt.white)
        self.grid = Qwt.QwtPlotGrid()
        self.grid.attach(self.plot)
        self.grid.setPen(QPen(Qt.black, 0, Qt.DotLine))
        self.curve = Qwt.QwtPlotCurve('')
        self.curve.setRenderHint(Qwt.QwtPlotItem.RenderAntialiased)
        self.pen = QPen(QColor('black'))
        self.pen.setWidth(0)
        self.curve.setPen(self.pen)
        self.curve.attach(self.plot)
        
    def connect_sig_slots(self):
        self.ui.start_button.clicked.connect(self.on_start)
        self.ui.stop_button.clicked.connect(self.on_stop)
        self.ui.clear_button.clicked.connect(self.on_clear)
        self.ui.action_save.triggered.connect(self.on_save)

    class WorkThread(QtCore.QThread):
        def __init__(self, pchan):
            QtCore.QThread.__init__(self)
            self.data = np.array([])
            self.phys_chan = pchan
            
        def start_daq(self):
            # Task parameters
            self.th = daqmx.TaskHandle()
            daqmx.CreateTask("", self.th)
            self.sr = 100.0
                
            daqmx.CreateAIVoltageChan(self.th, self.phys_chan, "", 
                                      daqmx.Val_Diff, -10.0, 10.0, 
                                      daqmx.Val_Volts, None)  
            daqmx.CfgSampClkTiming(self.th, "", self.sr, daqmx.Val_Rising, 
                                   daqmx.Val_ContSamps, 1000)
            daqmx.StartTask(self.th, fatalerror=False)

        def get_data(self):
            while True:
                # Parameters for analog read        
                samps_per_chan = int(self.sr/10)
                timeout = 10
                fillmode = daqmx.Val_GroupByChannel
                array_size_samps = 1000
                nchan = 1
                
                data1, spc = daqmx.ReadAnalogF64(self.th, samps_per_chan, 
                                                 timeout, fillmode, 
                                                 array_size_samps, nchan)
                                                 
                self.data = np.append(self.data, data1[:,0])
        
        def run(self):
            self.start_daq()
            self.get_data()
            
        def clear(self):
            daqmx.ClearTask(self.th)
            
    def on_start(self):
        self.clabel.setText("Starting... ")
        pchan = self.ui.combo_box.currentText()
        self.daqthread = self.WorkThread(str(pchan))
        self.daqthread.start()
        self.genthread = self.GenThread()
        self.genthread.start()
        time.sleep(0.1)
        self.timer.start(100)
        self.ui.start_button.setDisabled(True)
        self.ui.combo_box.setDisabled(True)
               
    def on_timer(self):
        text = str(len(self.daqthread.data)) + " points acquired "
        self.clabel.setText(text)
        self.update_plot()
        
    def update_plot(self):
        ydata = self.daqthread.data
        xdata = np.asarray(np.arange(len(ydata))/self.daqthread.sr)
        if len(ydata) == 0: 
            ydata = [np.nan]
            xdata = [np.nan]
            
        self.plot.setAxisScale(Qwt.QwtPlot.xBottom, 
                               max(xdata[-1] - 5, 0), max(5, xdata[-1]))
        self.curve.setData(xdata, ydata)
        self.plot.replot()
        
    def on_stop(self):
        if self.timer.isActive():
            self.timer.stop()
        if self.daqthread.isRunning():
            self.daqthread.clear()
        self.ui.start_button.setEnabled(True)
        self.ui.combo_box.setEnabled(True)
            
    def on_clear(self):
        self.curve.setData([np.nan], [np.nan])
        self.plot.replot()
        self.daqthread.data = np.array([])
        
    def on_save(self):
        np.save('npy/test_data', self.daqthread.data)
        
    def closeEvent(self, event):
        if self.timer.isActive():
            self.timer.stop()
        if self.daqthread.isRunning():
            self.daqthread.clear()
            
    class GenThread(QtCore.QThread):
        def __init__(self):
            QtCore.QThread.__init__(self)
        
        def run(self):
            wavegen.main(1)
        

def main():
    
    app = QtGui.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    
    sys.exit(app.exec_())
    

if __name__ == '__main__':
    main()