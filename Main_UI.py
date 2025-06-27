"""
File allowing to drive differents devices, in optic
of the EARLYBIRD research project : https://hal.science/hal-04663862v1
Include an user interface, if you don't want it, check the main.py file
"""
from Emulator import PSemu,OSCIemu,PPKemu
import time 
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FCTA 
import webbrowser
import threading
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

#____________functions use to control devices______________#   
def preparation(nbpente:int=2):        # nb of back and forward for the tension
    global ps,ppk,osci,El_osci_3
    try:
        tension = osci.waveforms[El_osci_3.get()]
    except NameError:  # If no test have been run, osci doesn't exist
        messagebox.showerror(title='No logs registered',message="You should run at least one test before that")
        return
    coup = len(tension)//nbpente
    tensionref = tension[:coup]
    if amp_source == 'PPK':
        courant = [el/1000 for el in ppk.log['Iout']]
    else:
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
    # If logs are empty, preparation will return None
    try:
        tension,courant1,courant2,P1,P2,diffc,diffp = preparation()
    except TypeError: # And then we abort the show function
        return
    fig,ax1 = plt.subplots()
    ax1.set_xlabel('Tension in V')
    ax1.plot(tension,courant1,ls='-',color='blue')
    ax1.plot(tension,courant2,ls=':',color='blue')
    ax1.plot(tension,diffc,ls='-',color='black')
    ax1.fill_between(tension,courant1,courant2,color='cyan',alpha=0.2)
    ax1.set_ylabel('Current in mA',color='blue',fontsize=15)

    ax2=ax1.twinx()
    ax2.plot(tension,P1,ls='-',color='red')
    ax2.plot(tension,P2,ls=':',color='red')
    ax2.plot(tension,diffp,ls='-',color='black')
    ax2.fill_between(tension,P1,P2,color='magenta',alpha=0.2)
    ax2.set_ylabel('Power in W',color='red',fontsize=15)

    plt.show()

def set_logs(n):
    pvemu.setLogInterval(n)
    ppkemu.setLogInterval(n)

def get_data():
    global ps,ppk,osci
    if amp_source=='PPK':
        ppk.measure()
    osci.measure()
    ps.measure()
       
def go_test():
    global pvemu,ppkemu,loader,amp_source,ps,ppk,osci
    ps = PSemu.PS(UI=True)        # Creation of object to communicate (Look PSemu.py)
    ps.connect_to_device()
    
    if amp_source=='PPK':
        ppk = PPKemu.PPK(UI=True)
        ppk.connect_to_device()
        ppk.setup()
        
    osci = OSCIemu.OSCI(UI=True)
    osci.connect_to_device()
    osci.set_channel(1,{"number":'1',"name":El_osci_3.get(),"probe_ratio":'1',"vertical_scale":El_osci_5.get(),"vertical_unit_name":El_osci_6.get(),"offset":El_osci_8.get(),"offset_unit_name":El_osci_9.get(),"display":"ON"})
    osci.setup()

    ps.setup(float(V_min.get()),1)    

    U=float(V_min.get())*100
    # A way to avoid weird approximations when increment with float, is to convert in integers
    # here for exemple, i multiply U by 100 (precision of power supply to cV) : 1.8 => 180
    # Then i add integer associated with the step (1 => +100, 0.1 => +10) (180 => 280, 180 => 190)
    # and divide by 100 for the Power supply command (280=>2.80, 190+>1.90)

    I = float(A_set.get())
    while U<float(V_max.get())*100:
        ps.setOperatingPoint(U/100,I) 
        time.sleep(0.1)
        get_data()
        U += 100*float(step.get())
        
    while U>float(V_min.get())*100:
        U -= 100*float(step.get())
        ps.setOperatingPoint(U/100,I)
        time.sleep(0.1)
        get_data()
        
#_______Other function for the UI_____________#
def openlink():
    webbrowser.open('https://owl.univ-nantes.fr')
        
#______________________Creation of the tkinter UI___________________________#
root = Tk()  # Create a new window
root.title("General control")
root.configure(bg="#82DAFF", padx=10, pady=10)

#///styling settings    
default_label_style = {"bg": "#82DAFF", "fg": "black", "highlightthickness": 0,"font": ("Arial", 12,"bold")}
default_entry_style = {"bg": "#ffffff", "fg": "black","font":("Impact",12),"width":10}
title_label_style = {"bg": "#BD63FF", "fg": "black", "highlightthickness": 0,"font": ("Courier new", 16,"bold"),"pady":5,"padx":35,"borderwidth":3,"relief":"solid"}
default_button_style = {"bg": "#ffffff", "fg": "black","font":("Impact",12,"italic")}

#/// creation of decoration images
menuPS = PhotoImage(file = r"UI_element/menu_PV.png").subsample(2,2)
menuPPK = PhotoImage(file = r"UI_element/menu_amp.png").subsample(2,2)
menuOSCI = PhotoImage(file = r"UI_element/menu_osci.png")
imgPS = PhotoImage(file = r"UI_element/Tenma.png").subsample(12,12)
imgPPK = PhotoImage(file = r"UI_element/Nordic.png").subsample(18,18)
imggraph = PhotoImage(file = r"UI_element/graphic.png").subsample(4,4)

Label(root,width=menuPS.width(),height=menuPS.height(),image=menuPS).grid(column=0,row=1,rowspan=5,columnspan=2) # menu image
    
#///part for a progressive/linear voltage (and a set current)
Label(root, text='Progressive set',**title_label_style).grid(column=2,columnspan=9,row=1)
Label(root,text='from',**default_label_style).grid(column=4,row=2)
V_min = ttk.Spinbox(root,width=10,from_=0,to=8,increment=0.01)
V_min.set(1.8) # default value
V_min.grid(column=5,columnspan=2,row=2)
Label(root,text='V',**default_label_style).grid(column=7,row=2)
Label(root,text='to',**default_label_style).grid(column=4,row=3)
V_max = ttk.Spinbox(root,width=10,from_=0,to=8,increment=0.01)
V_max.set(5) # default value
V_max.grid(column=5,columnspan=2,row=3)
Label(root,text='V',**default_label_style).grid(column=7,row=3)
Label(root,text='Step :',justify='right',**default_label_style).grid(column=3,columnspan=3,row=4)
step = ttk.Combobox(root,values=['1','0.1','0.01'],width=5,state='readonly')
step.current(1)
step.grid(column=6,columnspan=3,row=4)
Label(root,text='Enter Current',**default_label_style).grid(column=3,columnspan=3,row=5)
A_set = ttk.Spinbox(root,width=10,from_=0,to=2,increment=0.001)
A_set.set(0.01) # default value
A_set.grid(column=6,columnspan=3,row=5)

amp_source = StringVar()
amp_source.set('PS')
menu_amp = Label(root,height=menuPPK.height(),width=menuPPK.width(),image=menuPPK)
El_amp_1 = Label(root,text='Choose amperemeter source',**title_label_style)
El_amp_2 = Radiobutton(root,variable=amp_source,value='PS',text='Power Source',**default_label_style)
El_amp_3 = Radiobutton(root,variable=amp_source,value='PPK',text='Power Profiler',**default_label_style)
El_amp_4 = Label(root,width=imgPS.width(),height=imgPS.height(),image=imgPS,**default_label_style)
El_amp_5 = Label(root,width=imgPPK.width(),height=imgPPK.height(),image=imgPPK)

menu_osci = Label(root,height=menuOSCI.height(),width=menuOSCI.width(),image=menuOSCI)
El_osci_1 = Label(root,text='(1)',**title_label_style)
El_osci_2 = Label(root,text='name :',**default_label_style)
El_osci_3 = Entry(root,**default_entry_style)
El_osci_3.insert(END,'Albert')
El_osci_4 = Label(root,text='Vertical scale :',**default_label_style)
El_osci_5 = Entry(root,**default_entry_style)
El_osci_5.insert(END,'2')
El_osci_6 = ttk.Combobox(root, values=['V','mV'],width=5,state='readonly')
El_osci_6.current(0)
El_osci_7 = Label(root,text='offset :',**default_label_style)
El_osci_8 = Entry(root,**default_entry_style)
El_osci_8.insert(END,'0')
El_osci_9 = ttk.Combobox(root, values=['V','mV'],width=5,state='readonly')
El_osci_9.current(0)

El_amp_1.grid(column=2,row=6,columnspan=9)
El_amp_2.grid(column=2,row=7,columnspan=4)
El_amp_3.grid(column=6,row=7,columnspan=4)
El_amp_4.grid(column=2,row=8,columnspan=4)
El_amp_5.grid(column=6,row=8,columnspan=4)
menu_amp.grid(column=0,row=6,columnspan=2,rowspan=3)

El_osci_1.grid(column=2,row=9,rowspan=3)
El_osci_2.grid(column=3,row=9,rowspan=3)
El_osci_3.grid(column=4,row=9,rowspan=3)
El_osci_4.grid(column=5,row=9,rowspan=3)
El_osci_5.grid(column=6,row=9,rowspan=3)
El_osci_6.grid(column=7,row=9,rowspan=3)
El_osci_7.grid(column=8,row=9,rowspan=3)
El_osci_8.grid(column=9,row=9,rowspan=3)
El_osci_9.grid(column=10,row=9,rowspan=3)
menu_osci.grid(column=0,row=9,columnspan=2,rowspan=3)

Button(root,text='Go testing',command=go_test,**default_button_style).grid(column=0,columnspan=11,row=12)
Button(root,text='showresults',image=imggraph,compound="right",bg='#A10000',fg='#FFE9E9',bd=5,activebackground="#FF0000",command=showLogs).grid(column=0,columnspan=11,row=13)
Button(root,text='EARLYBIRD project page',bg='blue',fg='white',activebackground="#00FAFF",command=openlink,bd=5).grid(column=0,columnspan=11,row=14)

root.mainloop()
