#! /.venv/bin/python3
# -*- coding: UTF-8 -*-

import usbtmc
import sys

class OSCI:
    """class to emulate an oscilloscope
    Will not work if your device is on a /dev/ttyACMX instead od /dev/usbtmcX
    Go check OSCI_on_ACMX for that
    """
    
    def __init__(self,UI:bool=False):
        self.device=None
        self.log=[]
        self.ui=UI
    
    def connectToDevice(self):
        plugged_devices = usbtmc.list_devices()
        if len(plugged_devices) != 1:
            if len(plugged_devices) > 1:
                if self.ui:
                    messagebox.showerror(title='ERROR',message="Multiple oscilloscopes connected!")
                    self.connectToDevice()
                else:
                    sys.exit("Multiple oscilloscopes connected!")
            else:
                if self.ui:
                    messagebox.showerror(title='ERROR',message="No oscilloscope detected!")
                    self.connectToDevice()
                else:
                    sys.exit("No oscilloscope detected!")
        #... and connect to it.
        try:
            instr = plugged_devices[0]
            self.device = usbtmc.Instrument(instr.idVendor,instr.idProduct)  # Device we gonna communicate with
            if self.ui:
                messagebox.showinfo(title='Successfully connected',message="Found oscilloscope")
            else:
                print("Found oscilloscope")
        except:
            sys.exit("Error connecting with oscilloscope")
    
if __name__ == '__main__':  # For debug purpose, wont execute if imported as a library
    oscitest = OSCI()
    oscitest.connectToDevice()