"""
Few examples of what we can do with the devices use
in optic of the EARLYBIRD research project : https://hal.science/hal-04663862v1
"""

from Emulator import PSemu,PPKemu,OSCIemu
import time
import matplotlib.pyplot as plt
import threading

#_________plotting function_________#

def preparation(nbpente:int=2):
    tension = osci.waveforms['albert']
    coup = len(tension)//nbpente
    tensionref = tension[:coup]
    courant = ppk.log['Iout']
    courant1=[]
    courant2=[]
    P = [eli*elu for eli,elu in zip(tension,courant)]
    P1 = []
    P2 = []
    
    diffc = []
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
    
    return tensionref,courant1,courant2,P1,P2,diffc,diffp

def showLogs():
    tension,courant1,courant2,P1,P2,diffc,diffp = preparation()
    print(diffc,diffp)
    fig,ax1 = plt.subplots()
    ax1.set_xlabel('Tension in V')
    ax1.plot(tension,courant1,ls='-',color='blue')
    ax1.plot(tension,courant2,ls=':',color='blue')
    ax1.plot(tension,diffc,ls='-',color='black')
    ax1.fill_between(tension,courant1,courant2,color='cyan')
    ax1.set_ylabel('Current in mA')
    ax1.axvline(x=1.8,ls=':',color='green')
    ax1.axvline(x=3.3,ls=':',color='green')

    ax2=ax1.twinx()
    ax2.plot(tension,P1,ls='-',color='red')
    ax2.plot(tension,P2,ls=':',color='red')
    ax2.plot(tension,diffp,ls='-',color='black')
    ax2.fill_between(tension,P1,P2,color='magenta')
    ax2.set_ylabel('Power in W')

    plt.show()
    
def setlogs(n):
    ps.set_log_interval(n)
    osci.set_log_interval(n)
    ppk.set_log_interval(n)

def get_data():
    osci.measure()
    ps.measure()
    ppk.measure()
    temp.append(time.time()-start)
    
res = input("Waiting ... ")

ps=PSemu.PS()        # Creation of object to communicate (Look PSemu.py)
ppk = PPKemu.PPK()
osci = OSCIemu.OSCI()
ps.connectToSupply()
ppk.connectToDevice()
osci.connectToDevice()
osci.set_channel(1,{"number":'1',"name":"albert","probe_ratio":'1',"vertical_scale":'2',"vertical_unit_name":"V","offset":'0',"offset_unit_name":"V","display":"ON"})
ps.setup(1.8,1)
ppk.setup()
osci.setup()

U=1.8
mark1_1=0
mark1_2=0
mark2_1=0
mark2_2=0
start = time.time()
temp=[]

while U<5:
    ps.setOperatingPoint(U,1) 
    time.sleep(0.1)
    get_data()
    if U>1.8 and mark1_1==0:
        mark1_1 = time.time()-start
    if U>3.3 and mark1_2==0:
        mark1_2 = time.time()-start
    U += 0.05
    
while U>1.8:
    U -= 0.05
    ps.setOperatingPoint(U,1)
    time.sleep(0.1)
    get_data()
    if U<1.8 and mark2_1==0:
        mark2_1 = time.time()-start
    if U<3.3 and mark2_2==0:
        mark2_2 = time.time()-start

ppk.stop()
showLogs() 