#General Services Page
from tkinter import * 
import tkinter as tk
from PIL import ImageTk, Image
from tkinter import ttk
GDPage=tk.Tk()
main_frame=Frame(GDPage)
main_frame.pack(fill=BOTH, expand=1)
my_canvas = Canvas(main_frame)
my_canvas.pack(side=LEFT, fill=BOTH, expand=1)
my_scrollbar = ttk.Scrollbar(main_frame, orient=VERTICAL, command=my_canvas.yview)
my_scrollbar.pack(side=RIGHT, fill=Y)
my_canvas.configure(yscrollcommand=my_scrollbar.set)
my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion = my_canvas.bbox("all")))
second_frame = Frame(my_canvas)
my_canvas.create_window((0,0), window=second_frame, anchor="nw")
background=Canvas(second_frame,width=600,height=1045)
image=ImageTk.PhotoImage(Image.open("General Doctors Page.jpg"))
background.create_image(0,0,anchor='nw',image=image)
background.pack(expand=True,fill=BOTH)
GDPage.geometry('600x1000')
def button_hover1(a):
    johnVargheseButton["borderwidth"]=1
def button_hover_leave1(b):
    johnVargheseButton["borderwidth"]=0
def button_hover2(a):
    ushaMandaButton["borderwidth"]=1
def button_hover_leave2(b):
    ushaMandaButton["borderwidth"]=0
def button_hover3(a):
    jasminRajuButton["borderwidth"]=1
def button_hover_leave3(b):
    jasminRajuButton["borderwidth"]=0
def button_hover4(a):
    anandRadhakishanButton["borderwidth"]=1
def button_hover_leave4(b):
    anandRadhakishanButton["borderwidth"]=0
back=ImageTk.PhotoImage(Image.open("Back-Button-Logo.jpg"))
backButtonLabel=Label(image=back)
backButton=Button(second_frame,image=back,borderwidth=0,highlightthickness=0)
backButton.place(x=450,y=20)
user=ImageTk.PhotoImage(Image.open("User Logo.jpg"))
userButtonLabel=Label(image=user)
userButton=Button(second_frame,image=user,borderwidth=0,highlightthickness=0)
userButton.place(x=540,y=12)
johnVarghese=ImageTk.PhotoImage(Image.open("John Varghese.jpg"))
johnVargheseButtonLabel=Label(image=johnVarghese)
johnVargheseButton=Button(second_frame,image=johnVarghese,borderwidth=0,highlightthickness=0)
johnVargheseButton.place(x=0,y=138)
ushaManda=ImageTk.PhotoImage(Image.open("Usha Manda.jpg"))
ushaMandaButtonLabel=Label(image=ushaManda)
ushaMandaButton=Button(second_frame,image=ushaManda,borderwidth=0,highlightthickness=0)
ushaMandaButton.place(x=0,y=323)
jasminRaju=ImageTk.PhotoImage(Image.open("Jasmin Raju.jpg"))
jasminRajuButtonLabel=Label(image=jasminRaju)
jasminRajuButton=Button(second_frame,image=jasminRaju,borderwidth=0,highlightthickness=0)
jasminRajuButton.place(x=0,y=510)
anandRadhakishan=ImageTk.PhotoImage(Image.open("Anand Radhakishan.jpg"))
anandRadhakishanButtonLabel=Label(image=anandRadhakishan)
anandRadhakishanButton=Button(second_frame,image=anandRadhakishan,borderwidth=0,highlightthickness=0)
anandRadhakishanButton.place(x=0,y=696)
johnVargheseButton.bind("<Enter>",button_hover1)
johnVargheseButton.bind("<Leave>",button_hover_leave1)
ushaMandaButton.bind("<Enter>",button_hover2)
ushaMandaButton.bind("<Leave>",button_hover_leave2)
jasminRajuButton.bind("<Enter>",button_hover3)
jasminRajuButton.bind("<Leave>",button_hover_leave3)
anandRadhakishanButton.bind("<Enter>",button_hover4)
anandRadhakishanButton.bind("<Leave>",button_hover_leave4)



