###################################################################
#                                                                 #
#                    KLAB TremBox GUI v2                          #
#                  -----------------------                        #
#                           Ludo                                  #
#                                                                 #
###################################################################

#TODO : Try to merge all accelerometer call in one DONE
#TODO : Add Zoom Out Buttom DONE
#TODO : Find a way to stream time, maybe not on axis but add a 4th plot with a global timer 
#TODO : Add data export (log file csv ?)
#TODO : Check that everything can run for at least 30 min (manage data buffer??)
#TODO : implement camera...


import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import functools
import numpy as np
import random as rd
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.figure import Figure
from matplotlib.animation import TimedAnimation
from matplotlib.lines import Line2D
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import time
import threading
import board
import busio
import adafruit_adxl34x

'''Create main window class - Qt backend'''
class CustomMainWindow(QMainWindow):
    def __init__(self):
        super(CustomMainWindow, self).__init__()
        # Define the geometry of the main window
        self.setGeometry(300, 300, 800, 400)
        self.setWindowTitle("KlabTremBox_v1")
        # Create FRAME_A
        self.FRAME_A = QFrame(self)
        self.FRAME_A.setStyleSheet("QWidget { background-color: %s }" % QColor(255,255,255,255).name())
        self.LAYOUT_A = QGridLayout()
        self.FRAME_A.setLayout(self.LAYOUT_A)
        self.setCentralWidget(self.FRAME_A)
        # Place the zoom in  button
        self.zoomBtn = QPushButton(text = 'zoom in')
        self.zoomBtn.setFixedSize(100, 50)
        self.zoomBtn.clicked.connect(self.zoomBtnAction)
        self.LAYOUT_A.addWidget(self.zoomBtn, *(0,0))
        # Place the zoom out  button
        self.zoomOutBtn = QPushButton(text = 'zoom out')
        self.zoomOutBtn.setFixedSize(100, 50)
        self.zoomOutBtn.clicked.connect(self.zoomOutBtnAction)
        self.LAYOUT_A.addWidget(self.zoomOutBtn, *(1,0))
        # Place the matplotlib figure for X axis
        self.myFig = CustomFigCanvas()
        self.myFig.set_yaxis_label('X-axis')
        self.LAYOUT_A.addWidget(self.myFig, *(0,1))
        # Place the second figure for Y axis 
        self.myFig_Y = CustomFigCanvas()
        self.myFig_Y.set_yaxis_label('Y-axis')
        self.LAYOUT_A.addWidget(self.myFig_Y, *(1,1))
        # Place the second figure for Z axis 
        self.myFig_Z = CustomFigCanvas()
        self.myFig_Z.set_yaxis_label('Z-axis')
        self.LAYOUT_A.addWidget(self.myFig_Z, *(2,1))
        # Add the callbackfunc to ..
        #The trick is to pass the three function X, Y, Z to the same dataSendLoop function
        myDataLoop = threading.Thread(name = 'myDataLoop', target = dataSendLoop, daemon = True, args = (self.addData_callbackFunc,self.addData_callbackFunc_Y,self.addData_callbackFunc_Z,))
        myDataLoop.start()
        #Show the window
        self.show()
        return

    def zoomBtnAction(self):
        print("zoom in")
        self.myFig.zoomIn(5)
        self.myFig_Y.zoomIn(5)
        self.myFig_Z.zoomIn(5)
        return
    
    def zoomOutBtnAction(self):
        print('zoom out')
        self.myFig.zoomOut(5)
        self.myFig_Y.zoomOut(5)
        self.myFig_Z.zoomOut(5)
        return

    #addData_callbackFuncs : update values for plot - true callback 
    def addData_callbackFunc(self, value):
        # print("Add data: " + str(value))
        self.myFig.addData(value)
        return
    
    def addData_callbackFunc_Y(self, value):
        # print("Add data: " + str(value))
        self.myFig_Y.addData(value)
        return
    
    def addData_callbackFunc_Z(self, value):
        # print("Add data: " + str(value))
        self.myFig_Z.addData(value)
        return

''' End Class '''

'''Add a custom canvas: a matplotlib backend enmbed in the Qt GUI'''
class CustomFigCanvas(FigureCanvas, TimedAnimation):
    def __init__(self):
        self.addedData = []
        print(matplotlib.__version__)
        # The data
        self.xlim = 200
        self.n = np.linspace(0, self.xlim - 1, self.xlim)
        a = []
        b = []
        a.append(2.0)
        a.append(4.0)
        a.append(2.0)
        b.append(4.0)
        b.append(3.0)
        b.append(4.0)
        self.y = (self.n * 0.0) + 50
        # The window
        self.fig = Figure(figsize=(5,5), dpi=100)
        self.ax1 = self.fig.add_subplot(111)
        # self.ax1 settings
        self.ax1.set_ylabel('data')
        self.line1 = Line2D([], [], color='blue')
        self.line1_tail = Line2D([], [], color='red', linewidth=2)
        self.line1_head = Line2D([], [], color='red', marker='o', markeredgecolor='r')
        self.ax1.add_line(self.line1)
        self.ax1.add_line(self.line1_tail)
        self.ax1.add_line(self.line1_head)
        self.ax1.set_xlim(0, self.xlim - 1)
        self.ax1.set_ylim(-30, 30)
        FigureCanvas.__init__(self, self.fig)
        TimedAnimation.__init__(self, self.fig, interval = 50, blit = True)
        return
    
    def set_yaxis_label(self, label):
        self.ax1.set_ylabel(label)

    def new_frame_seq(self):
        return iter(range(self.n.size))

    def _init_draw(self):
        lines = [self.line1, self.line1_tail, self.line1_head]
        for l in lines:
            l.set_data([], [])
        return

    def addData(self, value):
        self.addedData.append(value)
        return
    

    def zoomIn(self, value):
        bottom = self.ax1.get_ylim()[0]
        top = self.ax1.get_ylim()[1]
        bottom += value
        top -= value
        self.ax1.set_ylim(bottom,top)
        self.draw()
        return
    
    def zoomOut(self, value):
        bottom = self.ax1.get_ylim()[0]
        top = self.ax1.get_ylim()[1]
        bottom -= value
        top += value
        self.ax1.set_ylim(bottom,top)
        self.draw()
        return

    def _step(self, *args):
        # Extends the _step() method for the TimedAnimation class.
        try:
            TimedAnimation._step(self, *args)
        except Exception as e:
            self.abc += 1
            print(str(self.abc))
            TimedAnimation._stop(self)
            pass
        return

    def _draw_frame(self, framedata):
        margin = 2
        while(len(self.addedData) > 0):
            self.y = np.roll(self.y, -1)
            self.y[-1] = self.addedData[0]
            del(self.addedData[0])

        self.line1.set_data(self.n[ 0 : self.n.size - margin ], self.y[ 0 : self.n.size - margin ])
        self.line1_tail.set_data(np.append(self.n[-10:-1 - margin], self.n[-1 - margin]), np.append(self.y[-10:-1 - margin], self.y[-1 - margin]))
        self.line1_head.set_data(self.n[-1 - margin], self.y[-1 - margin])
        self._drawn_artists = [self.line1, self.line1_tail, self.line1_head]
        return

''' End Class '''


# You need to setup a signal slot mechanism, to
# send data to your GUI in a thread-safe way.
# Believe me, if you don't do this right, things
# go very very wrong..
class Communicate(QObject):
    data_signal = pyqtSignal(float)

''' End Class '''
    
class Communicate_Y(QObject):
    data_signal_Y = pyqtSignal(float)

''' End Class '''

class Communicate_Z(QObject):
    data_signal_Z = pyqtSignal(float)

''' End Class '''


'''Create sendloop data for data streaming'''
def dataSendLoop(addData_callbackFunc,addData_callbackFunc_Y,addData_callbackFunc_Z):
    # Setup the signal-slot mechanism for all 3 channels.
    mySrc = Communicate()
    mySrc.data_signal.connect(addData_callbackFunc)
    
    mySrc_Y = Communicate_Y()
    mySrc_Y.data_signal_Y.connect(addData_callbackFunc_Y)
    
    mySrc_Z = Communicate_Z()
    mySrc_Z.data_signal_Z.connect(addData_callbackFunc_Z)

    #INITIATE ACCELEROMETER
    #Use prepare i2c connection for SCL/SDA pins
    i2c = busio.I2C(board.SCL, board.SDA)
    #instantiate ADXL library
    accelerometer = adafruit_adxl34x.ADXL345(i2c)
    #The starting time
    start = time.time()

    #Infinite loop, data will stream until you kill the process
    while(True):
        time.sleep(0.01)
        mySrc.data_signal.emit(accelerometer.acceleration[0]) # <- signal from X axis
        mySrc_Y.data_signal_Y.emit(accelerometer.acceleration[1]) # <- signal from Y axis
        mySrc_Z.data_signal_Z.emit(accelerometer.acceleration[2]) # <- signal from Z axis
        #mySrc.data_signal.emit(accelerometer.acceleration[2]) # <- signal from X axis
    ###
###



if __name__== '__main__':
    app = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create('Cleanlooks'))
    myGUI = CustomMainWindow()
    sys.exit(app.exec_())

