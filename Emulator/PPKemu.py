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
        self.logInterval = 0.005         # duration between logs, in s
        self.log = {}                    
        self.run = False
        self.port= ''
        self.duration=0
        self.ui = UI
        self.com = None
        
    def set_log_interval(self,duration):
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
        if len(plugged_devices) != 2:
            if len(plugged_devices) > 2:
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
            self.ps = serial.Serial(port=plugged_devices[1], baudrate=115200, timeout=1)
            time.sleep(0.2)
            self.ps.reset_input_buffer()
            self.port = plugged_devices[1]
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
    
    def setup(self):
        self.checkconnected()
        self.log['Iout'] = []
        self.com = PPK2_API(self.port, timeout=1, write_timeout=1, exclusive=True)
        try:
            self.com.get_modifiers()
        except:
            pass
        self.com.set_source_voltage(5)
        self.com.use_ampere_meter()  # set ampere meter mode
        self.com.toggle_DUT_power('ON')
        self.com.start_measuring()
        self.run = True
        
    def measure(self):
        read_data = self.com.get_data()
        if self.run:
            samples, raw_digital = self.com.get_samples(read_data)
            self.log['Iout'].append(sum(samples)/len(samples))
        else:
            print('Error : Amperemeter stopped')
            
    def stop(self):
        self.run = False
        self.com.stop_measuring()
        
if __name__ == '__main__':  # For debug purpose, wont execute if imported as a library
    ppktest = PPK()
    ppktest.connectToDevice()
    ppktest.setup()
    time.sleep(3)
    for i in range(5):
        ppktest.measure()
        time.sleep(0.01)
    print(ppktest.log)
    ppktest.stop()