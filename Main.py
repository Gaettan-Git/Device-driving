"""
Few examples of what we can do with the devices use
in optic of the EARLYBIRD research project : https://hal.science/hal-04663862v1
"""

from Emulator import PSemu,PPKemu,OSCIemu
import time
import matplotlib.pyplot as plt
import threading

#_________plotting function_________#
def showLogs():
    timei,Vcur,Icur,Vsup,Iusp = zip(*ps.log)
    
    print(len(temp),len(tension),len(courant))
    fig,ax1 = plt.subplots(nrows=2)
    ax1[0].plot(temp,courant,ls='-',color='red')
    ax1[0].set_ylabel('Current in mA')
    
    P=[]
    for i in range(min(len(tension),len(courant))):
        P.append(tension[i]*courant[i])
    ax2=ax1[0].twinx()
    ax2.plot(temp,P,ls='-',color='blue')
    ax2.set_ylabel('Power in W')
    
    ax1[1].plot(temp,tension,ls='-',color='black')
    ax1[1].set_xlabel('time of mesure')
    ax1[1].set_ylabel('Tension in V')
    plt.show()

def setlogs(n):
    ps.set_log_interval(n)
    osci.set_log_interval(n)
    #ppk.set_log_interval(n)

def measure():
    threading.Thread(target=get_data).start()
    
def get_data():
    try:
        temp.append(osci.waveforms['time'][-1])
    except:
        temp.append(0)
    try:
        tension.append(osci.waveforms['albert'][-1])
    except:
        tension.append(0)
    try:
        courant.append(ps.log[-1][2])
    except:
        courant.append(0)
res = input("Waiting ... ")

ps=PSemu.PS()        # Creation of object to communicate (Look PSemu.py)
#ppk = PPKemu.PPK()
osci = OSCIemu.OSCI()
ps.connectToSupply()
#ppk.connectToDevice()
osci.connectToDevice()

osci.setup()
osci.set_channel(1,{"number":1,"name":"albert","probe_ratio":1,"vertical_scale":1,"vertical_unit_name":"V","offset":1,"offset_unit_name":"V","display":"ON"})
#osci.set_channel(4,{"number":4,"name":"bertrand","probe_ratio":1,"vertical_scale":1,"vertical_unit_name":"V","offset":1.5,"offset_unit_name":"V","display":"ON"})
osci.set_time_to(1,'MS')
osci.set_trigger({"source":"CHANnel","source_number":1,"slope":0,"slope_unit":"V","threshold":1})
setlogs(0.005)

temp=[];tension=[];courant=[]

ps.start(0,1)
#ppk.startAmperemeter()
osci.start()
U=1.4

while U<5.5:
    U += 0.05
    ps.setOperatingPoint(U,1) # another Irradiance ..
    time.sleep(0.05)
    measure()
    
while U>1.4:
    U -= 0.05
    ps.setOperatingPoint(U,1)
    time.sleep(0.05)
    measure()
    
ps.stop()
#ppk.stop()
osci.stop()
osci.mainThread.join()
showLogs() 