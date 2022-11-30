#Main Page Code
from tkinter import * 
import tkinter as tk
from PIL import ImageTk, Image
MPage=tk.Tk()
background=Canvas(MPage,width=600,height=338)
image=ImageTk.PhotoImage(Image.open("Main-Page-Background.jpg"))
background.create_image(0,0,anchor='nw',image=image)
background.pack(expand=True,fill=BOTH)
MPage.title('Mindcology')
MPage.geometry('600x600')
MPage.configure(bg='white')
Login=Button(MPage,text='Login Here',font=('Bahnschrift Condensed',16),bg='white',fg='black',borderwidth=2, relief="solid")
Login.place(x=195, y=345)
Register=Button(MPage,text='Register Now',font=('Bahnschrift Condensed',16),bg='white',fg='black',borderwidth=2, relief="solid")
Register.place(x=295, y=345)
MPage.mainloop()
