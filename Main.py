"""
Few examples of what we can do with the devices use
in optic of the EARLYBIRD research project : https://hal.science/hal-04663862v1
"""

from Emulator import PVEmu,PPKemu,OSCIemu
import time
import matplotlib.pyplot as plt

#_________plotting function_________#
def showLogs():
    time = osci.waveforms['time']
    fig,ax1 = plt.subplots(nrows=2)
    timeppk,Imes=zip(*ppk.log)
    for key in osci.waveforms:
        if key =='time':
            pass
        elif osci.waveforms[key] != []:
            Vmes = osci.waveforms[key]
            ax1[0].plot(Vmes,[el*1000/float(res) for el in Vmes],ls=':',color='red')
            ax1[0].plot(Vmes,Imes,ls='-',color='red')
            ax1[0].set_ylabel('Current in mA')
            ax2=ax1[0].twinx()
            ax2.plot(Vmes,[(el/float(res))*el for el in Vmes],ls='-',color='blue')
            ax2.set_ylabel('Power in W')
            ax1[0].set_xlabel('Tension in V')
            
            ax1[1].plot(time,Vmes,ls='-',color='black')
            ax1[1].set_xlabel('time of mesure')
            ax1[1].set_ylabel('Tension in V')
    plt.show()

def setlogs(n):
    pv.set_log_interval(n)
    osci.set_log_interval(n)
    ppk.set_log_interval(n)
    
res = input("Enter the test resistance (ohm): ")

pv=PVEmu.PV()          # Creation of object to communicate (Look PVEmu.py)
ppk = PPKemu.PPK()
osci = OSCIemu.OSCI()
pv.connectToSupply()
ppk.connectToDevice()
osci.connectToDevice()
osci.setup()
osci.set_channel(1,{"number":1,"name":"albert","probe_ratio":1,"vertical_scale":1,"vertical_unit_name":"V","offset":1,"offset_unit_name":"V","display":"ON"})
#osci.set_channel(4,{"number":4,"name":"bertrand","probe_ratio":1,"vertical_scale":1,"vertical_unit_name":"V","offset":1.5,"offset_unit_name":"V","display":"ON"})
osci.set_time_to(1,'MS')
osci.set_trigger({"source":"CHANnel","source_number":1,"slope":0,"slope_unit":"V","threshold":1})
setlogs(0.005)
pv.start(0,0.1)
ppk.startAmperemeter()
osci.start()
for i in range(51):
    U = 0+i*0.1  
    pv.setOperatingPoint(U,0.1) # another Irradiance ..
    time.sleep(0.1)            
pv.stop()
ppk.stop()
osci.stop()
showLogs() 
