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
def showLogs():
    loader.trigger()

def set_logs(n):
    pvemu.setLogInterval(n)
    ppkemu.setLogInterval(n)

def get_data():
    global ps,ppk,osci
    if recquire_amp and amp_source=='PPK':
        ppk.measure()
    if recquire_osci:
        osci.measure()
    ps.measure()
       
def go_test():
    global recquire_amp,recquire_osci,pvemu,ppkemu,osciemu,loader,amp_source,ps,ppk,osci
    ps = PSemu.PS(UI=True)        # Creation of object to communicate (Look PSemu.py)
    ps.connectToSupply()
    
    if recquire_amp and amp_source=='PPK':
        ppk = PPKemu.PPK(UI=True)
        ppk.connectToDevice()
        ppk.setup()
    if recquire_osci:
        osci = OSCIemu.OSCI(UI=True)
        osci.connectToDevice()
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
        Add_amp.config(text="Amperemeter please !")
        El_amp_1.grid_forget()
        El_amp_2.grid_forget()
        El_amp_3.grid_forget()
        El_amp_4.grid_forget()
        El_amp_5.grid_forget()
        menu_amp.grid_forget()

def pop_osci_command():
    global recquire_osci,Add_osci,El_osci_1,El_osci_2,El_osci_3,El_osci_4,El_osci_5,El_osci_6,El_osci_7,El_osci_8,El_osci_9
    recquire_osci = not recquire_osci  # To do a 'switch function' allowing the on/off of amperemeter
    if recquire_osci:  # Button on : displaying elements of selection
        Add_osci.config(text="Nevermind, i don't want it")
        El_osci_1.grid(column=2,row=16)
        El_osci_2.grid(column=3,row=16)
        El_osci_3.grid(column=4,row=16)
        El_osci_4.grid(column=5,row=16)
        El_osci_5.grid(column=6,row=16)
        El_osci_6.grid(column=7,row=16)
        El_osci_7.grid(column=8,row=16)
        El_osci_8.grid(column=9,row=16)
        El_osci_9.grid(column=10,row=16)
        menu_osci.grid(column=0,row=16,columnspan=2,rowspan=3)
    else:
        Add_osci.config(text="oscilloscope please !")
        El_osci_1.grid_forget()
        El_osci_2.grid_forget()
        El_osci_3.grid_forget()
        El_osci_4.grid_forget()
        El_osci_5.grid_forget()
        El_osci_6.grid_forget()
        El_osci_7.grid_forget()
        El_osci_8.grid_forget()
        El_osci_9.grid_forget()
        menu_osci.grid_forget()
    
def openlink():
    webbrowser.open('https://hal.science/hal-04663862v1')
        
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
menuPV = PhotoImage(file = r"UI_element/menu_PV.png").subsample(2,2)
menuPPK = PhotoImage(file = r"UI_element/menu_amp.png").subsample(2,2)
menuOSCI = PhotoImage(file = r"UI_element/menu_osci.png")
imgPV = PhotoImage(file = r"UI_element/Tenma.png").subsample(12,12)
imgPPK = PhotoImage(file = r"UI_element/Nordic.png").subsample(18,18)
imggraph = PhotoImage(file = r"UI_element/graphic.png").subsample(4,4)

Label(root,width=menuPV.width(),height=menuPV.height(),image=menuPV).grid(column=0,row=0,rowspan=10,columnspan=2) # menu image
    
#///part for a progressive/linear voltage (and a set current)
Label(root, text='Progressive set',**title_label_style).grid(column=2,columnspan=9,row=1)
Label(root,text='from',**default_label_style).grid(column=2,columnspan=3,row=3)
V_min = ttk.Spinbox(root,width=10,from_=0,to=8,increment=0.01)
V_min.set(1.8) # default value
V_min.grid(column=5,columnspan=3,row=3)
Label(root,text='V',**default_label_style).grid(column=8,columnspan=3,row=3)
Label(root,text='to',**default_label_style).grid(column=2,columnspan=3,row=4)
V_max = ttk.Spinbox(root,width=10,from_=0,to=8,increment=0.01)
V_max.set(5) # default value
V_max.grid(column=5,columnspan=3,row=4)
Label(root,text='V',**default_label_style).grid(column=8,columnspan=3,row=4)
Label(root,text='Step :',justify='right',**default_label_style).grid(column=3,columnspan=3,row=5)
step = ttk.Combobox(root,values=['1','0.1','0.01'],width=5,state='readonly')
step.current(1)
step.grid(column=7,columnspan=3,row=5)
Label(root,text='Enter Current',**default_label_style).grid(column=3,columnspan=3,row=6)
A_set = ttk.Spinbox(root,width=10,from_=0,to=2,increment=0.001)
A_set.set(0.01) # default value
A_set.grid(column=7,columnspan=3,row=6)
Button(root,text='Go !',command=go_test,**default_button_style).grid(column=2,columnspan=9,row=8)

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

recquire_osci=False
menu_osci = Label(root,height=menuOSCI.height(),width=menuOSCI.width(),image=menuOSCI)
Add_osci = Button(root,text="oscilloscope please !",command=pop_osci_command,**default_button_style)
Add_osci.grid(column=0,row=15,columnspan=2)
El_osci_1 = Label(root,text='(1)',**title_label_style)
El_osci_2 = Label(root,text='name :',**default_label_style)
El_osci_3 = Entry(root,**default_entry_style)
El_osci_4 = Label(root,text='Vertical scale :',**default_label_style)
El_osci_5 = Entry(root,**default_entry_style)
El_osci_6 = ttk.Combobox(root, values=['V','mV'],width=5,state='readonly')
El_osci_6.current(0)
El_osci_7 = Label(root,text='offset :',**default_label_style)
El_osci_8 = Entry(root,**default_entry_style)
El_osci_9 = ttk.Combobox(root, values=['V','mV'],width=5,state='readonly')
El_osci_9.current(0)

Button(root,text='EARLYBIRD project page',bg='blue',fg='white',activebackground="#00FAFF",command=openlink,bd=5).grid(column=2,columnspan=9,row=0)
Button(root,text='showresults',image=imggraph,compound="right",bg='#A10000',fg='#FFE9E9',bd=5,activebackground="#FF0000",command=showLogs).grid(column=2,columnspan=9,row=28)

root.mainloop()