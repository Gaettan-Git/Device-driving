"""
Few examples of what we can do with the devices use
in optic of the EARLYBIRD research project : https://hal.science/hal-04663862v1
"""

from Emulator import PVEmu,PPKemu
import time
from matplotlib import pyplot as plt

#_________plotting function_________#
def showLogs():
    timepv,Vmes,Imes,Vref,Iref=zip(*pv.log)
    fig,axV=plt.subplots(nrows=2,figsize=(10,8))
    axV[0].plot(timepv,Vmes,ls='-',label='Tension mesurée',linewidth=3,color='blue')
    axV[0].set_ylabel('voltage V',fontsize=15)
    axV[0].set_xlabel('pv time',fontsize=15)
    axV[0].legend(loc='upper left',fontsize=15)
    if with_amp:
        timeppk,Iamp = zip(*ppk.log)
        Iamp = [i/1000 for i in Iamp]
        axV[1].plot(timeppk,Iamp,ls='-',label='mesured current (Power Profiler)',linewidth=3,color='red')
        axV[1].set_ylabel('current mA',fontsize=15)
        axV[1].set_ylim(0)
        axV[1].legend(loc='upper left',fontsize=15)
        axV[1].set_xlabel('ppk time',fontsize=15)
    else:
        axV[1].plot(timepv,Imes,ls='-',label='mesured current (Power Supply)',linewidth=3,color='red')
        axV[1].set_ylabel('current mA',fontsize=15)
        axV[1].set_ylim(0)
        axV[1].legend(loc='upper left',fontsize=15)
    plt.show()
    
print("1 : set a precise voltage and current to TENMA Power supply")
print("2 : progressive voltage for TENMA")
print("3 : progressive voltage, with Nordic PPK2 amperemeter")
print("3res : progressive voltage, PPK2 amperemeter, with a precise resistance")

choix = input("What are we doing ? ")

#__________________________#
if choix=='1':
    pv=PVEmu.PV()          # Creation of object to communicate (Look PVEmu.py)
    pv.connectToSupply()       
    pv.identification()         
    pv.setLogInterval(.005)    
    pv.start(3,0.1)            
    time.sleep(5)             
    pv.stop()
    with_amp=False
    showLogs()             
#__________________________#
if choix=='2':
    pv=PVEmu.PV()
    pv.connectToSupply()
    pv.identification()
    pv.setLogInterval(.005)        #log each 5ms
    pv.start(0.8,0.01)            # start thread: 3.3V, 0.01A
    for i in range(43):
        U = 0.8+i*0.1  
        pv.setOperatingPoint(U,0.5) # another Irradiance ..
        time.sleep(0.1)
    with_amp=False                         # also available with in list: pv.log
    pv.stop()
    showLogs()

#__________________________________#
if choix=='3':  
    def setlogs(n):  # log each n seconds for both devices
        pv.setLogInterval(n)
        ppk.setLogInterval(n)

    pv=PVEmu.PV()
    ppk = PPKemu.PPK()

    pv.connectToSupply()
    ppk.connectToDevice()

    setlogs(.005)        #log each 5ms
    ppk.startAmperemeter()         # start the amperemeter measures for the ppk2
    pv.start(0.8,0.01)
    for i in range(43):
        U = 0.8+i*0.1  
        pv.setOperatingPoint(U,0.5) # another Irradiance ..
        time.sleep(0.1)
    pv.stop()
    ppk.stop()
    with_amp=True
    showLogs()

#________________________________#
if choix=='3res':
    res = float(input('Which resistance (ohm) ? '))
    def showlogs():
        timepv,Vmes,Imes,Vref,Iref=zip(*pv.log)
        timeppk,Iamp = zip(*ppk.log)
        Iamp = [i/1000 for i in Iamp]
        Iattendu = [(j/res)*1000 for j in Vmes]
        fig,axV=plt.subplots(nrows=2,figsize=(10,8))
        axV[0].plot(timepv,Vmes,ls='-',label='Tension mesured',linewidth=3,color='blue')
        axV[0].set_ylabel('voltage V',fontsize=15)
        axV[0].set_xlabel('pv time',fontsize=15)
        axV[0].legend(loc='upper left',fontsize=15)
        axV[1].plot(timeppk,Iamp,ls='-',label='Currant mesured',linewidth=3,color='red')
        axV[1].plot(timepv,Iattendu,ls='-',label='Current expected (I=U/R)',color='green')
        axV[1].set_ylabel('current mA',fontsize=15)
        axV[1].set_ylim(0)
        axV[1].legend(loc='upper left',fontsize=15)
        plt.show()    

    def setlogs(n):  # log each n seconds for both devices
        pv.setLogInterval(n)
        ppk.setLogInterval(n)

    pv=PVEmu.PV()
    ppk = PPKemu.PPK()

    pv.connectToSupply()
    ppk.connectToDevice()

    setlogs(.005)        #log each 5ms
    ppk.startAmperemeter()         # start the amperemeter measures for the ppk2
    pv.start(0.8,0.8/res)
    for i in range(43):
        U = 0.8+i*0.1  
        pv.setOperatingPoint(U,0.5) # another Irradiance ..
        time.sleep(0.1)
    pv.stop()
    ppk.stop()
    with_amp=True
    showlogs()
    
elif choix=='debug':
    ppk = PPKemu.PPK() 
    ppk.connectToDevice()
    ppk.setLogInterval(.005)
    ppk.startAmperemeter()         # start the amperemeter measures for the ppk2
    time.sleep(6)
    ppk.stop()
    timeppk,Iamp = zip(*ppk.log)
    Iamp = [i/1000 for i in Iamp]
    fig,axV=plt.subplots()
    axV.plot(timeppk,Iamp)
    axV.set_xlabel('time')
    axV.set_ylabel('current mA')
    plt.show()