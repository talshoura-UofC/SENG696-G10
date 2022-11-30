#Workshops Page
from tkinter import * 
import tkinter as tk
from PIL import ImageTk, Image
from tkinter import ttk
WPage=tk.Tk()
main_frame=Frame(WPage)
main_frame.pack(fill=BOTH, expand=1)
my_canvas = Canvas(main_frame)
my_canvas.pack(side=LEFT, fill=BOTH, expand=1)
my_scrollbar = ttk.Scrollbar(main_frame, orient=VERTICAL, command=my_canvas.yview)
my_scrollbar.pack(side=RIGHT, fill=Y)
my_canvas.configure(yscrollcommand=my_scrollbar.set)
my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion = my_canvas.bbox("all")))
second_frame = Frame(my_canvas)
my_canvas.create_window((0,0), window=second_frame, anchor="nw")
background=Canvas(second_frame,width=600,height=1445)
image=ImageTk.PhotoImage(Image.open("Workshops Page.jpg"))
background.create_image(0,0,anchor='nw',image=image)
background.pack(expand=True,fill=BOTH)
WPage.geometry('600x1000')
def button_hover1(a):
    addictionExtinctionButton["borderwidth"]=1
def button_hover_leave1(b):
    addictionExtinctionButton["borderwidth"]=0
def button_hover2(a):
    absolutAnxietyButton["borderwidth"]=1
def button_hover_leave2(b):
    absolutAnxietyButton["borderwidth"]=0
def button_hover3(a):
    dawnOverDepressionButton["borderwidth"]=1
def button_hover_leave3(b):
    dawnOverDepressionButton["borderwidth"]=0
def button_hover4(a):
    againstTraumaButton["borderwidth"]=1
def button_hover_leave4(b):
    againstTraumaButton["borderwidth"]=0
def button_hover5(a):
    adiosAddictionButton["borderwidth"]=1
def button_hover_leave5(b):
    adiosAddictionButton["borderwidth"]=0
def button_hover6(a):
    feelingAndHealingButton["borderwidth"]=1
def button_hover_leave6(b):
    feelingAndHealingButton["borderwidth"]=0
back=ImageTk.PhotoImage(Image.open("Back-Button-Logo.jpg"))
backButtonLabel=Label(image=back)
backButton=Button(second_frame,image=back,borderwidth=0,highlightthickness=0)
backButton.place(x=450,y=20)
user=ImageTk.PhotoImage(Image.open("User Logo.jpg"))
userButtonLabel=Label(image=user)
userButton=Button(second_frame,image=user,borderwidth=0,highlightthickness=0)
userButton.place(x=540,y=12)
addictionExtinction=ImageTk.PhotoImage(Image.open("Addiction Extinction.jpg"))
addictionExtinctionButtonLabel=Label(image=addictionExtinction)
addictionExtinctionButton=Button(second_frame,image=addictionExtinction,borderwidth=0,highlightthickness=0)
addictionExtinctionButton.place(x=0,y=138)
absolutAnxiety=ImageTk.PhotoImage(Image.open("Absolut Anxiety.jpg"))
absolutAnxietyButtonLabel=Label(image=absolutAnxiety)
absolutAnxietyButton=Button(second_frame,image=absolutAnxiety,borderwidth=0,highlightthickness=0)
absolutAnxietyButton.place(x=0,y=323)
dawnOverDepression=ImageTk.PhotoImage(Image.open("Dawn Over Depression.jpg"))
dawnOverDepressionButtonLabel=Label(image=dawnOverDepression)
dawnOverDepressionButton=Button(second_frame,image=dawnOverDepression,borderwidth=0,highlightthickness=0)
dawnOverDepressionButton.place(x=0,y=510)
againstTrauma=ImageTk.PhotoImage(Image.open("Against Trauma.jpg"))
againstTraumaButtonLabel=Label(image=againstTrauma)
againstTraumaButton=Button(second_frame,image=againstTrauma,borderwidth=0,highlightthickness=0)
againstTraumaButton.place(x=0,y=696)
adiosAddiction=ImageTk.PhotoImage(Image.open("Adios Addiction.jpg"))
adiosAddictionButtonLabel=Label(image=adiosAddiction)
adiosAddictionButton=Button(second_frame,image=adiosAddiction,borderwidth=0,highlightthickness=0)
adiosAddictionButton.place(x=0,y=879)
feelingAndHealing=ImageTk.PhotoImage(Image.open("Feeling and Healing.jpg"))
feelingAndHealingButtonLabel=Label(image=feelingAndHealing)
feelingAndHealingButton=Button(second_frame,image=feelingAndHealing,borderwidth=0,highlightthickness=0)
feelingAndHealingButton.place(x=0,y=1064)
addictionExtinctionButton.bind("<Enter>",button_hover1)
addictionExtinctionButton.bind("<Leave>",button_hover_leave1)
absolutAnxietyButton.bind("<Enter>",button_hover2)
absolutAnxietyButton.bind("<Leave>",button_hover_leave2)
dawnOverDepressionButton.bind("<Enter>",button_hover3)
dawnOverDepressionButton.bind("<Leave>",button_hover_leave3)
againstTraumaButton.bind("<Enter>",button_hover4)
againstTraumaButton.bind("<Leave>",button_hover_leave4)
adiosAddictionButton.bind("<Enter>",button_hover5)
adiosAddictionButton.bind("<Leave>",button_hover_leave5)
feelingAndHealingButton.bind("<Enter>",button_hover6)
feelingAndHealingButton.bind("<Leave>",button_hover_leave6)



