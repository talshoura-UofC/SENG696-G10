#Special Services Page
from tkinter import * 
import tkinter as tk
from PIL import ImageTk, Image
from tkinter import ttk
SDPage=tk.Tk()
main_frame=Frame(SDPage)
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
image=ImageTk.PhotoImage(Image.open("Specialists Page.jpg"))
background.create_image(0,0,anchor='nw',image=image)
background.pack(expand=True,fill=BOTH)
SDPage.geometry('600x1000')
def button_hover1(a):
    diyaMoreButton["borderwidth"]=1
def button_hover_leave1(b):
    diyaMoreButton["borderwidth"]=0
def button_hover2(a):
    tarunMatthewButton["borderwidth"]=1
def button_hover_leave2(b):
    tarunMatthewButton["borderwidth"]=0
def button_hover3(a):
    karimLokButton["borderwidth"]=1
def button_hover_leave3(b):
    karimLokButton["borderwidth"]=0
def button_hover4(a):
    vijayGaneshanButton["borderwidth"]=1
def button_hover_leave4(b):
    vijayGaneshanButton["borderwidth"]=0
def button_hover5(a):
    ananyaBahriButton["borderwidth"]=1
def button_hover_leave5(b):
    ananyaBahriButton["borderwidth"]=0
def button_hover6(a):
    radhikaRamanathanButton["borderwidth"]=1
def button_hover_leave6(b):
    radhikaRamanathanButton["borderwidth"]=0
back=ImageTk.PhotoImage(Image.open("Back-Button-Logo.jpg"))
backButtonLabel=Label(image=back)
backButton=Button(second_frame,image=back,borderwidth=0,highlightthickness=0)
backButton.place(x=450,y=20)
user=ImageTk.PhotoImage(Image.open("User Logo.jpg"))
userButtonLabel=Label(image=user)
userButton=Button(second_frame,image=user,borderwidth=0,highlightthickness=0)
userButton.place(x=540,y=12)
diyaMore=ImageTk.PhotoImage(Image.open("Diya More.jpg"))
diyaMoreButtonLabel=Label(image=diyaMore)
diyaMoreButton=Button(second_frame,image=diyaMore,borderwidth=0,highlightthickness=0)
diyaMoreButton.place(x=0,y=138)
tarunMatthew=ImageTk.PhotoImage(Image.open("Dr. Tarun Matthew.jpg"))
tarunMatthewButtonLabel=Label(image=tarunMatthew)
tarunMatthewButton=Button(second_frame,image=tarunMatthew,borderwidth=0,highlightthickness=0)
tarunMatthewButton.place(x=0,y=323)
karimLok=ImageTk.PhotoImage(Image.open("Karim Lok.jpg"))
karimLokButtonLabel=Label(image=karimLok)
karimLokButton=Button(second_frame,image=karimLok,borderwidth=0,highlightthickness=0)
karimLokButton.place(x=0,y=510)
vijayGaneshan=ImageTk.PhotoImage(Image.open("Vijay Ganeshan.jpg"))
vijayGaneshanButtonLabel=Label(image=vijayGaneshan)
vijayGaneshanButton=Button(second_frame,image=vijayGaneshan,borderwidth=0,highlightthickness=0)
vijayGaneshanButton.place(x=0,y=696)
ananyaBahri=ImageTk.PhotoImage(Image.open("Ananya Bahri.jpg"))
ananyaBahriButtonLabel=Label(image=ananyaBahri)
ananyaBahriButton=Button(second_frame,image=ananyaBahri,borderwidth=0,highlightthickness=0)
ananyaBahriButton.place(x=0,y=879)
radhikaRamanathan=ImageTk.PhotoImage(Image.open("Radhika Ramanathan.jpg"))
radhikaRamanathanButtonLabel=Label(image=radhikaRamanathan)
radhikaRamanathanButton=Button(second_frame,image=radhikaRamanathan,borderwidth=0,highlightthickness=0)
radhikaRamanathanButton.place(x=0,y=1064)
diyaMoreButton.bind("<Enter>",button_hover1)
diyaMoreButton.bind("<Leave>",button_hover_leave1)
tarunMatthewButton.bind("<Enter>",button_hover2)
tarunMatthewButton.bind("<Leave>",button_hover_leave2)
karimLokButton.bind("<Enter>",button_hover3)
karimLokButton.bind("<Leave>",button_hover_leave3)
vijayGaneshanButton.bind("<Enter>",button_hover4)
vijayGaneshanButton.bind("<Leave>",button_hover_leave4)
ananyaBahriButton.bind("<Enter>",button_hover5)
ananyaBahriButton.bind("<Leave>",button_hover_leave5)
radhikaRamanathanButton.bind("<Enter>",button_hover6)
radhikaRamanathanButton.bind("<Leave>",button_hover_leave6)



