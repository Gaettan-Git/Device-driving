#! /.venv/bin/python3
# -*- coding: UTF-8 -*-

import time
import sys
import threading
import pyvisa
from tkinter import *
from tkinter import messagebox

# Arranged version of code from https://github.com/mbriday/PVEmu/tree/main
# with tkinter UI integration, and pyvisa commands
# some code from http://www.pinon-hebert.fr/Knowledge/index.php/TENMA_72_2705

class PS:
    """ class to emulate a PV+MPPT, 
    based on the TENMA programmable power supply
    """

    def __init__(self,UI:bool = False):
        self.ps = None                   # handler to the serial port
        self.logInterval = 0.005         # duration between logs, in s
        self.log = []                    # tuple (date(s), voltage ,current, actualVoltage, actualCurrent)
        self.voltageSetpoint = 0.0       # V
        self.currentSetpoint = 0.0       # I
        self.mainThread = None
        self.dataLock = threading.Lock()
        self.run = False                 #thread is running
        self.com = None
        self.ui=UI
        
    def connectToSupply(self):
        self.ps = None
        rm = pyvisa.ResourceManager()
        try:
            import serial
            import serial.tools.list_ports
            import serial.serialutil
        except ImportError:
            print("The 'serial' python package is not installed");
            print("Please install first the package (Linux, Mac, Win, …)")
            print("here: https://pythonhosted.org/pyserial/index.html")
            sys.exit(1)
        #find ports...
        ports = serial.tools.list_ports.comports()
        devicesPS = [port.device for port in ports if port.product == 'USB Virtual COM']
        if len(devicesPS) != 1:
            if len(devicesPS) > 1:
                if self.ui:
                    messagebox.showerror(title='ERROR',message="Too many power supplies detected!")
                    self.connectToSupply()
                else:
                    sys.exit("Too many power supplies detected!")
            else:
                if self.ui:
                    messagebox.showerror(title='ERROR',message="No power supply detected")
                    self.connectToSupply()
                else:
                    sys.exit("No power supply detected!")
        #... and connect to it.
        try:
            self.ps = serial.Serial(port=devicesPS[0], baudrate=115200, timeout=1)
            #we flush the input buffer.
            # https://stackoverflow.com/questions/7266558/pyserial-buffer-wont-flush
            time.sleep(0.2)
            self.ps.reset_input_buffer()
            #no output for now
            self.com = rm.open_resource('ASRL'+devicesPS[0]+'::INSTR')
            self.setOutput(False)
            if self.ui:
                messagebox.showinfo(title='Successfully connected',message="Found power supply : {0}".format(self.identification()))
            else:
                print("Found power supply : {0}".format(self.identification()))
        except serial.serialutil.SerialException: 
            sys.exit('Serial line {0} not found'.format(devicesPS[0]))

    def checkconnected(self):
        if not self.ps:
            sys.stderr.write ("ERROR: you should first connect to the power supply")
            sys.exit(1)
        elif not self.ps.isOpen():
            sys.stderr.write ("ERROR: try to work on closed port "+self.ps.name()+"\n")
            sys.exit(1)

    def setOperatingPoint(self,voltage, amp):
        self.checkconnected()
        with self.dataLock:
            self.voltageSetpoint = voltage
            self.currentSetpoint = amp
        self.com.write('VSET1:'+str(voltage)+'\n')
        self.com.write('ISET1:'+str(amp)+'\n')

    def getOperatingPoint(self):
        self.checkconnected()
        V = float(self.com.query('VOUT1?\n'))
        I = float(self.com.query('IOUT1?\n'))
        return (V,I)

    def reset(self):
        self.checkconnected()
        self.com.write(b'*RST\n')

    def identification(self):
        self.checkconnected()
        return self.com.query('*IDN?')

    def setOutput(self,state):
        self.checkconnected()
        if state:
            self.com.write('OUT1\n')
        else:
            self.com.write('OUT0\n')

    def set_log_interval(self,duration):
        """ define the duration between 2 logs
        If the duration is too low, the thread witll go as fast as possible.
        """
        with self.dataLock:
            self.logInterval = duration
            
    def start(self, Vinit, Iinit):
        if self.mainThread:
            sys.stderr.write('ERROR: power supply already started!')
        else:
            # setup ..
            self.checkconnected()
            self.setOperatingPoint(Vinit,Iinit)
            self.setOutput(True)
            self.log = []
            # .. and run
            self.mainThread = threading.Thread(target=self.mainLoop)
            self.run = True
            self.mainThread.start()

    def stop(self):
        self.run = False

    def mainLoop(self):
        startDate = time.time()
        while self.run:
            #measure
            (Vcur,Icur) = self.getOperatingPoint()
            #log
            with self.dataLock:
                self.log.append((time.time()-startDate,Vcur,Icur,self.voltageSetpoint,self.currentSetpoint))
        #closing…
        stopDate=time.time()
        self.duration = stopDate-startDate
        self.setOutput(False)
        self.ps.close()
        self.mainThread = None
        
if __name__ == '__main__':  # For debug purpose, wont execute if imported as a library
    pstest = PS()
    pstest.connectToSupply()
    pstest.setOutput(True)
    