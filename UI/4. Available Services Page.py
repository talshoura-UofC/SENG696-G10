#Available Services Page
from tkinter import * 
import tkinter as tk
from PIL import ImageTk, Image
SPage=tk.Tk()
background=Canvas(SPage,width=600,height=600)
image=ImageTk.PhotoImage(Image.open("Services Page.jpg"))
background.create_image(0,0,anchor='nw',image=image)
background.pack(expand=True,fill=BOTH)
SPage.geometry('600x600')
def button_hover1(a):
    generalDoctorsButton["borderwidth"]=1
def button_hover_leave1(b):
    generalDoctorsButton["borderwidth"]=0
def button_hover2(a):
    specialDoctorsButton["borderwidth"]=1
def button_hover_leave2(b):
    specialDoctorsButton["borderwidth"]=0
def button_hover3(a):
    workshopsButton["borderwidth"]=1
def button_hover_leave3(b):
    workshopsButton["borderwidth"]=0
back=ImageTk.PhotoImage(Image.open("Back-Button-Logo.jpg"))
backButtonLabel=Label(image=back)
backButton=Button(SPage,image=back,borderwidth=0,highlightthickness=0)
backButton.place(x=450,y=20)
user=ImageTk.PhotoImage(Image.open("User Logo.jpg"))
userButtonLabel=Label(image=user)
userButton=Button(SPage,image=user,borderwidth=0,highlightthickness=0)
userButton.place(x=550,y=12)
generalDoctors=ImageTk.PhotoImage(Image.open("General Doctors Label.jpg"))
generalDoctorsButtonLabel=Label(image=generalDoctors)
generalDoctorsButton=Button(SPage,image=generalDoctors,borderwidth=0,highlightthickness=0)
generalDoctorsButton.place(x=0,y=170)
specialDoctors=ImageTk.PhotoImage(Image.open("Specialists Label.jpg"))
specialDoctorsButtonLabel=Label(image=specialDoctors)
specialDoctorsButton=Button(SPage,image=specialDoctors,borderwidth=0,highlightthickness=0)
specialDoctorsButton.place(x=0,y=309)
workshops=ImageTk.PhotoImage(Image.open("Workshops Label.jpg"))
workshopsButtonLabel=Label(image=workshops)
workshopsButton=Button(SPage,image=workshops,command=user,borderwidth=0,highlightthickness=0)
workshopsButton.place(x=0,y=447)
generalDoctorsButton.bind("<Enter>",button_hover1)
generalDoctorsButton.bind("<Leave>",button_hover_leave1)
specialDoctorsButton.bind("<Enter>",button_hover2)
specialDoctorsButton.bind("<Leave>",button_hover_leave2)
workshopsButton.bind("<Enter>",button_hover3)
workshopsButton.bind("<Leave>",button_hover_leave3)



