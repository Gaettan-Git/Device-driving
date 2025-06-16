#! /.venv/bin/python3
# -*- coding: UTF-8 -*-

import pyvisa
import sys
import os
import time
import csv
from tkinter import messagebox
from decimal import Decimal

class Scale:
    """Act as a scale referance, for differant unit"""
    def __init__(self):
        self.time = {'S':1,'MS':1e-3,'US':1e-6,'NS':1e-9}
        self.frequency = {'Hz':1,'KHz':1e3}
        
class Config:
    """class to handle configurations of the machine"""
    def __init__(self):   
        self.channels = [
            {"number":1,"name":"CH1","probe_ratio":1,"vertical_scale":500,"vertical_unit_name":"mV","offset":0,"offset_unit_name":"V","display":"OFF"},
            {"number":2,"name":"CH2","probe_ratio":1,"vertical_scale":500,"vertical_unit_name":"mV","offset":0,"offset_unit_name":"V","display":"OFF"},
            {"number":3,"name":"CH3","probe_ratio":1,"vertical_scale":500,"vertical_unit_name":"mV","offset":0,"offset_unit_name":"V","display":"OFF"},
            {"number":4,"name":"CH4","probe_ratio":1,"vertical_scale":500,"vertical_unit_name":"mV","offset":0,"offset_unit_name":"V","display":"OFF"}
            ]
        self.trigger = {"source":"CHANnel","source_number":1,"slope":1,"slope_unit":"V","threshold":1}
        self.timescale = (200,'US')
        self.frequency = (1,'KHz')
        
class OSCI:
    """class to emulate an oscilloscope
    Will not work if your device is on a /dev/ttyACMX instead od /dev/usbtmcX
    Go check OSCI_on_ACMX for that
    """
    
    def __init__(self,UI:bool=False):
        self.com = None
        self.config = Config()
        self.scale = Scale()
        self.waveforms = {}
        self.ui = UI
    
    def float_to_nr3(self,number:float) -> str:
        """Convert float to scientific notation (NR3 format)."""
        return f"{Decimal(number):.1E}"

    def time_to_nr3(self, value: int, time_base:str) -> str:
        """Convert time to NR3 format using a time base unit.""" 
        number = float(value * self.scale.time[time_base])
        return self.float_to_nr3(number)
    
    def connectToDevice(self):
        rm = pyvisa.ResourceManager()
        try:
            self.com = rm.open_resource('USB0::10893::918::CN62117164::0::INSTR')
            if self.ui:
                messagebox.showinfo(title='Successfully connected',message="Found oscilloscope")
            else:
                print("Found oscilloscope")
        except:
            if self.ui:
                messagebox.showerror(title='Connection problem',message="Error occured while attempting connect to device")
            else:
                sys.exit("Error connecting with oscilloscope")
    
    def setup(self):
        """Set up the device with provided configuration."""
        try:
            self._setup_acquisition()
            self._setup_time_base()
            self._setup_channels()
            self._setup_trigger()
        except KeyboardInterrupt:
            self.release()
    
    def display_text(self, text:str='',color:str='CH1',background:str='OPAQue'):
        """Display text on the screen"""
        self.com.write(":DISPlay:ANNotation:BACKground "+background)
        self.com.write(":DISPlay:ANNotation:COLor "+color)
        self.com.write(":DISPlay:ANNotation:TEXT '"+text+"'")
        
    def _reset_device(self):
        """
        Reset device to it's default state.
        Ensure oscilloscope is in a known state before configuration.
        """
        self.com.write("*RST")
        self.com.write("*CLS")
        self.com.write(":STOP")
        self.com.write(":MEASure:CLEar")
        self.display_text()
        for ch in range(1, 5):
            self.com.write(f":CHANnel{ch}:DISPlay OFF")
    
    def _write(self,cond:str=":DISPlay:ANNotation:TEXT ''"):
        """
        Wtitting method for instrument
        """
        if self.com == None:
            sys.exit("You need to connect to oscilloscope first !")
        try:
            self.com.write(cond)
        except Exception as e:
            print("Error while writting instruction : %s",e)
            
    def _get(self,ques:str='*IDN?'):
        """
        query method for instrument
        """
        try:
            return self.com.query(ques)
        except:
            print("Error while query :",ques)
    
    def _setup_time_base(self):
        """
        Set up time base, in time/division
        Note: Device has 10 horizontal divisions
        """
        scale = self.time_to_nr3(self.config.timescale[0],self.config.timescale[1])
        self._write(f":TIMebase:SCALe {scale}")
        self._write(":TIMebase:REFerence LEFT")
        self._write(":TIMebase:POSition 0")

    def _setup_acquisition(self,mode:str="NORMal"):
        """Set up acquisition mode"""
        self._write(":ACQuire:TYPE "+mode)

    def _setup_channels(self):
        """Set up channels parameters"""
        for ch in self.config.channels:
            self._write(f":CHANnel{ch['number']}:COUPling DC")
            self._write(f":CHANnel{ch['number']}:UNITs VOLT")

            probe_ratio = self.float_to_nr3(ch["probe_ratio"])
            self._write(f":CHANnel{ch['number']}:PROBe {probe_ratio}")

            scale_str = self.float_to_nr3(ch["vertical_scale"])
            self._write(f":CHANnel{ch['number']}:SCALe {scale_str}{ch['vertical_unit_name']}")

            offset_str = self.float_to_nr3(ch["offset"])
            self._write(f":CHANnel{ch['number']}:OFFSet {offset_str}{ch['offset_unit_name']}")

            self._write(f":CHANnel{ch['number']}:DISPlay {ch['display']}")
            self._write(f":CHANnel{ch['number']}:LABel '{ch['name']}'")

        self._write(":DISPlay:LABel ON")
    
    def _setup_trigger(self):
        """Set up trigger parameters"""
        trig = self.config.trigger
        self._write(":TRIGger:MODE EDGE")
        self._write(f":TRIGger:EDGE:SOURce {trig['source']}{trig['source_number']}")
        self._write(f":TRIGger:EDGE:SLOPe {trig['slope']}{trig['slope_unit']}")
        self._write(f":TRIGger:EDGE:LEVel {self.float_to_nr3(trig['threshold'])}")
    
    def _acquire_data(self):
        """Acquire data from device by waiting for trigger event to be detected."""
        try:
            self._write(":WAVeform:FORMat ASCII")
            self._write(":WAVeform:POINts:MODE MAXimum")

            # Calculate the number of points based on the horizontal scale and required frequency
            time_range = (
                10 * self.config.timescale[0] * self.scale.time[self.config.timescale[1]]
            )
            freq = self.config.frequency[0] * self.scale.frequency[self.config.frequency[1]]
            num_points = int(time_range * freq)
            self._write(f":WAVeform:POINts {num_points}")

            self._get("*OPC?")
            self._write(":SINGLE")

            while True:
                cond = int(self._get(":OPERegister:CONDition?"))
                if (cond & 0b1000) == 0:
                    break
                time.sleep(0.001)
                
        except Exception as e:
            print("Acquisition error %s", e)
            
    def set_channel_setting(self,setname,setvalue,number:int=1):
        """
        Change a channel setting to desired value
        """
        self.config.channels[number-1][setname] = setvalue
        self._setup_channels()  # to apply changes
    
    def set_channel(self,number:int,param:dict):
        self.config.channels[number-1] = param
        self._setup_channels()
        
    def set_trigger_parameter(self,setname:str,setvalue):
        """
        change a trigger setting to desired value
        """
        self.config.trigger[setname] = setvalue
        self._setup_trigger()
    
    def set_trigger(self,param:dict):
        self.config.trigger = param
        self._setup_trigger()
        
    def set_time_to(self,num:float,unit:str):
        """
        set to a defined timescale
        """
        self.config.timescale = (num,unit)
        self._setup_time_base()
    
    def collect(self):
        """Collect data"""
        try:
            self._acquire_data()
            for ch in self.config.channels:
                if ch["display"]=='ON':
                    self._write(f":WAVeform:SOURce CHANnel{ch['number']}")
                    raw_data = self._get(":WAVeform:DATA?").strip()
                try:
                    values = [float(v) for v in raw_data.split(",")[1:]]
                    self.waveforms[ch['name']] = values
                except Exception as e:
                    self.waveforms[ch['name']] = []

        except KeyboardInterrupt:
            self.release()
    
    def run(self):
        self.com.write(":RUN")
        
    def release(self):
        self.com.close()
        
if __name__ == '__main__':  # For debug purpose, wont execute if imported as a library
    oscitest = OSCI()
    oscitest.connectToDevice()
    oscitest.setup()
    oscitest.release()