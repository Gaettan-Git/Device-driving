"""
Few examples of what we can do with the devices use
in optic of the EARLYBIRD research project : https://hal.science/hal-04663862v1
"""

from Emulator import PSemu,PPKemu,OSCIemu
import time
import matplotlib.pyplot as plt
import threading

#_________plotting function_________#

def preparation(nbpente:int=2):        # nb of back and forward for the tension
    tension = osci.waveforms['albert']
    coup = len(tension)//nbpente
    tensionref = tension[:coup]
    courant = [el*1000 for el in ps.log['Iout']] # Conversion from uA to mA
    courant1=[]    # 1 for the incrementation phase
    courant2=[]    # 2 for the decrementation phase
    P = [eli*elu for eli,elu in zip(tension,courant)]
    P1 = []
    P2 = []
    
    diffc = []   # Differences of power consumption between increment and decrement voltage 
    diffp = []
    for i in range(coup):
        courant1.append(courant[i])
        courant2.append(courant[-1-i])
        P1.append(P[i])
        P2.append(P[-1-i])        
        calc = (courant1[i]+courant2[i])/2
        diffc.append(calc)
        calc = (P1[i]+P2[i])/2
        diffp.append(calc)
    
    return tensionref,courant1,courant2,P1,P2,diffc,diffp  # data treated, ready for plot

def showLogs():
    tension,courant1,courant2,P1,P2,diffc,diffp = preparation()
    fig,ax1 = plt.subplots()
    ax1.set_xlabel('Tension in V')
    ax1.plot(tension,courant1,ls='-',color='blue')
    ax1.plot(tension,courant2,ls=':',color='blue')
    ax1.plot(tension,diffc,ls='-',color='black')
    ax1.fill_between(tension,courant1,courant2,color='cyan',alpha=0.2)
    ax1.set_ylabel('Current in mA',color='blue',font=("Courier new", 16,"bold"))
    ax1.axvline(x=1.8,ls=':',color='green')
    ax1.axvline(x=3.3,ls=':',color='green')

    ax2=ax1.twinx()
    ax2.plot(tension,P1,ls='-',color='red')
    ax2.plot(tension,P2,ls=':',color='red')
    ax2.plot(tension,diffp,ls='-',color='black')
    ax2.fill_between(tension,P1,P2,color='magenta',alpha=0.2)
    ax2.set_ylabel('Power in W',color='red',font=("Courier new", 16,"bold"))

    plt.show()
    
def setlogs(n):
    ps.set_log_interval(n)
    osci.set_log_interval(n)
    ppk.set_log_interval(n)

def get_data():     # Call measurement methods in Emulator classes
    osci.measure()
    ps.measure()
    ppk.measure()
    
res = input("Waiting ... ")

# Creation of objects to communicate
ps=PSemu.PS()        
ppk = PPKemu.PPK()
osci = OSCIemu.OSCI()
# Connection with the differant devices
ps.connect_to_device()
ppk.connect_to_device()
osci.connect_to_device()
# Setting up for measures
osci.set_channel(1,{"number":'1',"name":"albert","probe_ratio":'1',"vertical_scale":'2',"vertical_unit_name":"V","offset":'0',"offset_unit_name":"V","display":"ON"})
ps.setup(1.8,1)
ppk.setup()
osci.setup()
time.sleep(0.5) # to be sure everyone is ready
U=180   # work with int, to avoid weird python approximation when incrementing in float (+0.05)

while U<500:
    U += 5
    ps.setOperatingPoint(U/100,1)   # convert in V (180 = 1.80 V)
    time.sleep(0.1)
    get_data()
        
while U>180:
    U -= 5
    ps.setOperatingPoint(U/100,1)
    time.sleep(0.1)
    get_data()

# Close communication
ps.release()
ppk.release()
osci.release()
showLogs() 