#Confirmation Page Code
from tkinter import * 
import tkinter as tk
from PIL import ImageTk, Image
from tkcalendar import *
CPage=tk.Tk()
background=Canvas(CPage,width=600,height=600)
image=ImageTk.PhotoImage(Image.open("Confirmation Page.jpg"))
background.create_image(0,0,anchor='nw',image=image)
background.pack(expand=True,fill=BOTH)
CPage.geometry('600x600')
def selected():
    print(var.get())
var=tk.StringVar()
ade=Radiobutton(CPage,text='Addiction Extinction - Rs1499/session',font=('Bahnschrift Condensed',14),variable=var,value='Addiction Extinction',command=selected,tristatevalue=0,bg="black",fg="gold")
ade.place(x=15,y=280)
aa=Radiobutton(CPage,text='Absolut Anxiety - Rs1499/session',font=('Bahnschrift Condensed',14),variable=var,value='Absolute Anxiety',command=selected,tristatevalue=0,bg="black",fg="gold")
aa.place(x=15,y=330)
at=Radiobutton(CPage,text='Against Trauma- Rs1499/session',font=('Bahnschrift Condensed',14),variable=var,value='Against Trauma',command=selected,tristatevalue=0,bg="black",fg="gold")
at.place(x=15,y=380)
dod=Radiobutton(CPage,text='Dawn Over Depression- Rs1499/session',font=('Bahnschrift Condensed',14),variable=var,value='Dawn Over Depression',command=selected,tristatevalue=0,bg="black",fg="gold")
dod.place(x=15,y=430)
fah=Radiobutton(CPage,text='Feeling and Healing - Rs1499/session',font=('Bahnschrift Condensed',14),variable=var,value='Feeling and Healing',command=selected,tristatevalue=0,bg="black",fg="gold")
fah.place(x=15,y=480)
ada=Radiobutton(CPage,text='Adios Addiction - Rs1499/session',font=('Bahnschrift Condensed',14),variable=var,value='Adios Addiction',command=selected,tristatevalue=0,bg="black",fg="gold")
ada.place(x=15,y=530)
cal=Calendar(CPage,selectmode="day",year=2021,month=8,day=22)
cal.place(x=317,y=300)
submit=ImageTk.PhotoImage(Image.open("Submit Button.jpg"))
submitButtonLabel=Label(image=submit)
submitButton=Button(CPage,image=submit,borderwidth=0,highlightthickness=0,command=submit)
submitButton.place(x=380,y=520)
