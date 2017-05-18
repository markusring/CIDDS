# -*- coding: utf-8 -*-
import sys
import mainscript
from Tkinter import *

def send_values(l1, l2, v1, v2, v3, e):
	mainscript.init(l1, l2, v1, v2, v3, e)
	sys.exit(0)

def main():
	master = Tk()
	master.title("generate dummy")
	
	#scripts
	t1 = Label(master, text="Which Scripts do you want to activate?", font="Verdana 10 bold")
	t1.grid(row=0,column=0)
	#checkboxes
	v1 = IntVar()
	Checkbutton(master, text="Browsing", variable=v1).grid(row=1, column=0, sticky=W)
	v2 = IntVar()
	Checkbutton(master, text="Mails", variable=v2).grid(row=2, column=0, sticky=W)
	v3 = IntVar()
	Checkbutton(master, text="Print", variable=v3).grid(row=3, column=0, sticky=W)
	
	Label(master, text=" ").grid(row=4,column=0)
	
	#personality
	t2 = Label(master, text="Descripe the personality of the dummy.", font="Verdana 10 bold")
	t2.grid(row=5,column=0)
	
	#level of lazyness
	t3 = Label(master, text="lazy\t\t")
	t3.grid(row=6,column=0)
	l1 = Scale(master, from_=0, to=10, length=600, tickinterval=5, orient=HORIZONTAL)
	l1.set(5)
	l1.grid(row=6,column=1)
	t4 = Label(master, text="\tactive\t\t")
	t4.grid(row=6,column=2)
	
	
	#level of private activities
	t5 = Label(master, text="private\t\t")
	t5.grid(row=8,column=0)
	l2 = Scale(master, from_=0, to=10, length=600, tickinterval=5, orient=HORIZONTAL)
	l2.set(5)
	l2.grid(row=8,column=1)
	t6 = Label(master, text="\tbusiness\t\t")
	t6.grid(row=8,column=2)
	
	Label(master, text=" ").grid(row=9,column=0)
	
	#counter of activities
	t7 = Label(master, text="How many activities should be executed?")
	t7.grid(row=10, column=1)
	e1 = Entry(master)
	e1.grid(row=11, column=1)

	Label(master, text=" ").grid(row=12,column=0)	

	#start dummy
	Button(master, text='Go', command=lambda:send_values(l1.get(), l2.get(),
			v1.get(), v2.get(), v3.get(), int(e1.get()))).grid(row=13,column=1)
	
	Label(master, text=" ").grid(row=14,column=0)
	
	mainloop()

if __name__ == "__main__":
	main()	
