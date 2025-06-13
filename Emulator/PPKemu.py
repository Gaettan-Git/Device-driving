#! /.venv/bin/python3
# -*- coding: UTF-8 -*-

import time
import sys
import threading
from ppk2_api.ppk2_api import PPK2_API
from tkinter import *
from tkinter import messagebox

class PPK:
    """ class to emulate a PPK device
    intended for the nordic ppk2
    """
    def __init__(self,UI:bool=False):
        self.ps = None                   # handler to the serial port
        self.logInterval = 0.100         # duration between logs, in s
        self.log = []                    # tuple (date(s),current,actualCurrent)
        self.port= ''
        self.duration=0
        self.mainThread = None           #Thread handler.
        self.dataLock = threading.Lock()
        self.run = False                 #thread is running
        self.ui = UI
        
    def setLogInterval(self,duration):
        """ define the duration between 2 logs
        If the duration is too low, the thread witll go as fast as possible.
        """
        with self.dataLock:
            self.logInterval = duration
            
    def connectToDevice(self):
        self.ps = None
        try:
            import serial
            import serial.tools.list_ports
        except ImportError:
            print("The 'serial' python package is not installed");
            print("Please install first the package (Linux, Mac, Win, …)")
            print("here: https://pythonhosted.org/pyserial/index.html")
            sys.exit(1)
        #find ports...
        ports = serial.tools.list_ports.comports()
        plugged_devices = PPK2_API.list_devices()
        if len(plugged_devices) != 1:
            if len(plugged_devices) > 1:
                if self.ui:
                    messagebox.showerror(title='ERROR',message="Multiple power profiler kit connected!")
                    self.connectToDevice()
                else:
                    sys.exit("Multiple power profiler kit connected!")
            else:
                if self.ui:
                    messagebox.showerror(title='ERROR',message="No power profiler kit detected!")
                    self.connectToDevice()
                else:
                    sys.exit("No power profiler kit detected!")
        #... and connect to it.
        try:
            self.ps = serial.Serial(port=plugged_devices[0], baudrate=115200, timeout=1)
            time.sleep(0.2)
            self.ps.reset_input_buffer()
            self.port = plugged_devices[0]
            if self.ui:
                messagebox.showinfo(title='Successfully connected',message="Found PPK2 at {0}".format(plugged_devices[0]))
            else:
                print("Found PPK2 at {0}".format(plugged_devices[0]))
        except serial.serialutil.SerialException:
            print('Serial line {0} not found'.format(plugged_devices[0]))  
            sys.exit(1)
    
    def checkconnected(self):
        if not self.ps:
            sys.stderr.write ("ERROR: you should first connect to the power supply")
            sys.exit(1)
        elif not self.ps.isOpen():
            sys.stderr.write ("ERROR: try to work on closed port "+self.ps.name()+"\n")
            sys.exit(1)    
    
    def startAmperemeter(self):
        if self.mainThread:
            sys.stderr.write('ERROR: power profile kit already measuring!')
        else:
            # setup ..
            self.checkconnected()
            self.log = []
            # .. and run
            self.mainThread = threading.Thread(target=self.mainLoopAmp)
            self.run = True
            self.mainThread.start()
    
    def mainLoopAmp(self):
        startDate = time.time()
        deadline = startDate+self.logInterval
        ppk2_test = PPK2_API(self.port, timeout=1, write_timeout=1, exclusive=True)
        ppk2_test.get_modifiers()
        ppk2_test.set_source_voltage(1)
        ppk2_test.use_ampere_meter()  # set ampere meter mode
        ppk2_test.start_measuring()
        #time.sleep(0.5)  # average delay on the amperemeter start
        while self.run:
            #periodicity
            time.sleep(max(0,deadline-time.time()))
            deadline += self.logInterval
            #measure
            average_A= 0  # by default, if shown it mean error
            read_data = ppk2_test.get_data()
            if read_data != b'':
                samples = ppk2_test.get_samples(read_data)[0]
                average_A = sum(samples)/len(samples)
            with self.dataLock:
                self.log.append((time.time()-startDate,average_A))
            #print("at {0} s we got {1} \n".format(time.time()-startDate,average_A))
        #closing…
        ppk2_test.stop_measuring()
        stopDate=time.time()
        self.ps.close()
        self.duration=stopDate-startDate
        self.mainThread = None
    
    def stop(self):
        self.run=False
        
if __name__ == '__main__':  # For debug purpose, wont execute if imported as a library
    ppktest = PPK()
    ppktest.connectToDevice()