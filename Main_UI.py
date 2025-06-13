"""
File allowing to drive differents devices, in optic
of the EARLYBIRD research project : https://hal.science/hal-04663862v1
Include an user interface, if you don't want it, check the main.py file
"""

global recquire_amp,amp_source,Add_amp,El_amp_1,El_amp_2,El_amp_3,El_amp_4,El_amp_5,menu_amp,loader

from Emulator import PVEmu,PPKemu
import time 
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FCTA 
import webbrowser
import threading
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

#____________functions use to control devices______________#   
def set_logs(n):
    pvemu.setLogInterval(n)
    ppkemu.setLogInterval(n)

def set_Voltage():
    global recquire_amp,pvemu,ppkemu,loader
    loader.trigger()
    pvemu=PVEmu.PV(UI=True)
    ppkemu=PPKemu.PPK(UI=True)
    pvemu.connectToSupply()
    if recquire_amp and amp_source.get()=='PPK':
            ppkemu.connectToDevice()
            ppkemu.startAmperemeter()
    set_logs(.005)
    U = float(V_set.get())
    I = float(A_set.get())   
    pvemu.start(U,I)
    time.sleep(float(timing.get()))
    pvemu.stop()
    if recquire_amp and amp_source.get()=='PPK':
        ppkemu.stop()
    loader.trigger()

def progressive_Voltage():
    global recquire_amp,pvemu,ppkemu
    pvemu=PVEmu.PV(UI=True)
    ppkemu=PPKemu.PPK(UI=True)
    pvemu.connectToSupply()
    if recquire_amp and amp_source.get()=='PPK':
        ppkemu.connectToDevice()
        ppkemu.startAmperemeter()    
    s=float(V_start.get())
    e=float(V_end.get())
    st = float(step.get())
    pvemu.setLogInterval(.005)        #log each 5ms
    pvemu.start(s,0.01)            # start thread: 3.3V, 0.01A
    steps = int(((e-s)/st)+1)
    for i in range(steps):
        U = s+i*st
        pvemu.setOperatingPoint(U,0.5) # another Irradiance ..
        time.sleep(float(timing.get())/steps)
    pvemu.stop()
    if recquire_amp and amp_source.get()=='PPK':
        ppkemu.stop()
        
#_______Other function for the UI_____________#
def pop_amp_command():
    global recquire_amp,amp_source,Add_amp,El_amp_1,El_amp_2,El_amp_3,El_amp_4,El_amp_5,menu_amp
    recquire_amp= not recquire_amp  # To do a 'switch function' allowing the on/off of amperemeter
    if recquire_amp:  # Button on : displaying elements of selection
        Add_amp.config(text="Nevermind, i don't want it")
        El_amp_1.grid(column=2,row=12,columnspan=9)
        El_amp_2.grid(column=2,row=13,columnspan=4)
        El_amp_3.grid(column=7,row=13,columnspan=4)
        El_amp_4.grid(column=2,row=14,columnspan=4)
        El_amp_5.grid(column=7,row=14,columnspan=4)
        menu_amp.grid(column=0,row=12,columnspan=2,rowspan=3)
    else:
        Add_amp.config(text="Apmeremeter please !")
        El_amp_1.grid_forget()
        El_amp_2.grid_forget()
        El_amp_3.grid_forget()
        El_amp_4.grid_forget()
        El_amp_5.grid_forget()
        menu_amp.grid_forget()

def pop_osci_command():
    print()
    

def openlink():
    webbrowser.open('https://hal.science/hal-04663862v1')

def showLogs():
    global pvemu,ppkemu
    try:
        timepv,Vmes,Imes,Vref,Iref=zip(*pvemu.log)
        if recquire_amp:
            fig,axV = plt.subplots(nrows=2,figsize=(10,8))
            axV[0].plot(timepv,Vmes,ls='-',label='Tension mesurée',linewidth=3,color='blue')
            axV[0].set_ylabel('voltage V',fontsize=15)
            axV[0].set_xlabel('time',fontsize=15)
            axV[0].legend(loc='upper left',fontsize=15)
            if amp_source.get()=='PPK':
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
        else:
            fig,axV = plt.subplots()
            axV.plot(timepv,Vmes,ls='-',label='Tension mesurée',linewidth=3,color='blue')
            axV.set_ylabel('voltage V',fontsize=15)
            axV.set_xlabel('time',fontsize=15)
            axV.legend(loc='upper left',fontsize=15)
        result = Toplevel(root)
        result.title("Result Figure")
        canvas = FCTA(fig,master=result)          
        canvas.get_tk_widget().pack()
        result.mainloop
    except NameError:
        messagebox.showerror(title='ERROR',message='You should run at least 1 test before')

class Load:
    def __init__(self,master,col,row):
        self.nature = Label(master,text='(/)',**default_label_style)
        self.show = False
        self.pos = (col,row)
    
    def loadloop(self):
        while True:
            if self.show:
                self.nature.grid(column=self.pos[0],row=self.pos[1])
            else:
                self.nature.grid_forget()
            loading.config(text="(--)")
            time.sleep(0.2)
            loading.config(text="(y)")
            time.sleep(0.2)
            loading.config(text="(/)")
            time.sleep
            
    def trigger(self):
        self.show= not self.show
        
#______________________Creation of the tkinter UI___________________________#
root = Tk()  # Create a new window
root.title("General control")
root.configure(bg="#82DAFF", padx=10, pady=10)

#/// settings to declare how the window will comport when distorded


#///styling settings    
default_label_style = {"bg": "#82DAFF", "fg": "black", "highlightthickness": 0,"font": ("Arial", 12,"bold")}
default_entry_style = {"bg": "#ffffff", "fg": "black","font":("Impact",12),"width":10}
title_label_style = {"bg": "#BD63FF", "fg": "black", "highlightthickness": 0,"font": ("Courier new", 16,"bold"),"pady":5,"padx":35,"borderwidth":3,"relief":"solid"}
default_button_style = {"bg": "#ffffff", "fg": "black","font":("Impact",12,"italic")}

#/// creation of decoration images
menuPV = PhotoImage(file = r"UI_element/menu_PV.png")
menuPPK = PhotoImage(file = r"UI_element/menu_amp.png")
imgPV = PhotoImage(file = r"UI_element/Tenma.png").subsample(9,9)
imgPPK = PhotoImage(file = r"UI_element/Nordic.png").subsample(12,12)
imggraph = PhotoImage(file = r"UI_element/graphic.png").subsample(4,4)

Label(root,width=menuPV.width(),height=menuPV.height(),image=menuPV).grid(column=0,row=0,rowspan=10,columnspan=2) # menu image

#///part for a precise set of voltage and current
Label(root, text='  For a precise set  ',**title_label_style).grid(column=2,columnspan=4,row=1)
Label(root,text='Enter Voltage',**default_label_style).grid(column=2,columnspan=2,row=3)
V_set = ttk.Spinbox(root,width=10,from_=0,to=8,increment=0.01)
V_set.set(1) # default value
V_set.grid(column=4,columnspan=2,row=3)
Label(root,text='Enter Current',**default_label_style).grid(column=2,columnspan=2,row=6)
A_set = ttk.Spinbox(root,width=10,from_=0,to=2,increment=0.001)
A_set.set(0.01) # default value
A_set.grid(column=4,columnspan=2,row=6)
Button(root,text='Set !',command=set_Voltage,**default_button_style).grid(column=2,columnspan=4,row=8)

#///Decorative sake
Label(root,text='OR',**title_label_style).grid(column=6,row=1,rowspan=9)
    
#///part for a progressive/linear voltage (and a set current)
Label(root, text='For a progressive set',**title_label_style).grid(column=7,columnspan=4,row=1)
Label(root,text='from',**default_label_style).grid(column=7,row=3)
V_start = ttk.Spinbox(root,width=10,from_=0,to=8,increment=0.01)
V_start.set(0.8) # default value
V_start.grid(column=8,row=3)
Label(root,text='V',**default_label_style).grid(column=9,row=3)
Label(root,text='to',**default_label_style).grid(column=7,row=4)
V_end = ttk.Spinbox(root,width=10,from_=0,to=8,increment=0.01)
V_end.set(5) # default value
V_end.grid(column=8,row=4)
Label(root,text='V',**default_label_style).grid(column=9,row=4)
Label(root,text='Step :',**default_label_style).grid(column=7,columnspan=2,row=5)
step = ttk.Combobox(root, values=['1','0.1','0.01'],width=5,justify='center',state='readonly')
step.current(1)
step.grid(column=9,row=5)
Label(root,text='Enter Current',**default_label_style).grid(column=7,row=6,columnspan=2)
A_set = ttk.Spinbox(root,width=10,from_=0,to=2,increment=0.001)
A_set.set(0.01) # default value
A_set.grid(column=9,row=6,columnspan=2)
Button(root,text='Go !',command=progressive_Voltage,**default_button_style).grid(column=7,columnspan=4,row=8)

#/// part for control of time
timing = Scale(root,label='time of testing (s)',length=400,orient='horizontal',from_=0.1,to=10,resolution=0.1,**default_label_style)
timing.set(5)
timing.grid(column=2,columnspan=9,row=16)


#///part for the on/off of amperemeter
amp_source = StringVar()
amp_source.set('PV')
recquire_amp=False
menu_amp = Label(root,height=menuPPK.height(),width=menuPPK.width(),image=menuPPK)
Add_amp = Button(root,text="Amperemeter please",command=pop_amp_command,**default_button_style)
Add_amp.grid(column=0,row=11,columnspan=2)
El_amp_1 = Label(root,text='Choose amperemeter source',**title_label_style)
El_amp_2 = Radiobutton(root,variable=amp_source,value='PV',text='Power Source',**default_label_style)
El_amp_3 = Radiobutton(root,variable=amp_source,value='PPK',text='Power Profiler',**default_label_style)
El_amp_4 = Label(root,width=imgPV.width(),height=imgPV.height(),image=imgPV,**default_label_style)
El_amp_5 = Label(root,width=imgPPK.width(),height=imgPPK.height(),image=imgPPK)

Add_osci = Button(root,text="oscilloscope please",command=pop_osci_command,**default_button_style)
Add_osci.grid(column=0,row=15,columnspan=2)

Button(root,text='EARLYBIRD project page',bg='blue',fg='white',activebackground="#00FAFF",command=openlink,bd=5).grid(column=2,columnspan=9,row=0)
Button(root,text='showresults',image=imggraph,compound="right",bg='#A10000',fg='#FFE9E9',bd=5,activebackground="#FF0000",command=showLogs).grid(column=2,columnspan=9,row=17)
loader = Load(root,6,9)

root.mainloop()