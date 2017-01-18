#!/usr/bin/env python

import rospy
import time

from Tkinter import *
import os
import tkFileDialog 
import tkMessageBox
import cPickle as pickle 
import threading 
from main_hrl import Hrl
from main_rl import Rl
from main_rl import createRL
def createWindowNewSim():
	mainWindow.withdraw()
	global newSimWindow
	newSimWindow = Toplevel(mainWindow)
	newSimWindow.title("Nouvelle simulation")
	newSimWindow.protocol("WM_DELETE_WINDOW", on_closing)
	Label(newSimWindow, text="Veuillez choisir le type d'apprentissage").pack()
	v = IntVar()
	btn = Radiobutton(newSimWindow, text="RL",variable=v, value=1, command=lambda: choiceSimul(0))
	btn.pack()
	btn.select()
	Radiobutton(newSimWindow, text="HRL",variable=v, value=2 ,command=lambda: choiceSimul(1)).pack()

	global btnGo 
	btnGo = Button(newSimWindow, text="Go", command=lambda: choiceSimul())
	btnGo.config(state="disabled")
	btnGo.pack()
	       
def choiceSimul(vall=-1):
	global choice 
	if(vall==-1):
		startSimul(choice)
	else:
		btnGo.config(state="normal")
		choice = vall

def startSimul(numSimul):
	global h
	global myTread
	if(numSimul==0):
		print("-----Start RL-----")
		h = Rl()
		#h.rl_loop()
		simulationWindows(numSimul,0)
		myTread = threading.Thread(target=h.rl_loop)
		myTread.start()
		#simulationWindow.mainloop()
		
	elif(numSimul==1):
		print("-----Start HRL-----")
		h = Hrl()
		simulationWindows(numSimul,0)
		myTread = threading.Thread(target=h.hrl_loop)
		myTread.start()
		
	else:
		print("ERROR")	

def loadSimulation():
	opts = {}
	opts['filetypes'] = [('HRL files', '*.hrl'), ('RL files', '*.rl')]
	opts['initialdir'] = './'
	opts['title'] = "Selection d'un fichier d'apprentissage"	
	path= tkFileDialog.askopenfilename(**opts)
	if(not path):return
	extension = path.split(".")[-1]
	myfile = open(path, "rb")
	global choice
	global h

	if(extension == "rl"):
		print("--It's RL file ")
		choice = 0
		dico = pickle.load(myfile)
		h = createRL(dico)
		myfile.close()	
		simulationWindows(choice,1)
		myTread = threading.Thread(target=h.rl_loop)
		myTread.start()		
	elif(extension == "hrl"):
		print("--It's HRL file ")
		choice = 1
		print("----NOT IMPLEMENTED----")
		return		
		#dico = pickle.load(myfile)
		#h = createHRL(dico)
		#myfile.close()	
		#simulationWindows(choice,1)
		#myTread = threading.Thread(target=h.hrl_loop)
		#myTread.start()		
	else:
		print("Error")                          
	
		
def simulationWindows(typeSimul,parent):
	print("-simulationWindows : "+str(typeSimul) )
	global h
	#newSimWindow.destroy()
	#newSimWindow.quit()
	if(parent==0):
		newSimWindow.withdraw()
	else:
		mainWindow.withdraw()
	
	global simulationWindow
	simulationWindow = Toplevel(mainWindow)
	simulationWindow.protocol("WM_DELETE_WINDOW", on_closing)
	if(typeSimul==0):
		simulationWindow.title("RL Simulation")
	elif(typeSimul==1):
		simulationWindow.title("HRL Simulation")
	else:
		simulationWindow.title("")
	Button(simulationWindow, text="Stopper la simulation", command=lambda: stopSimulation(True)).pack()
	Button(simulationWindow, text="Stopper et sauvegarder la simulation", command=lambda: stopAndSave()).pack()

def stopSimulation(stopW):
	global h
	result = tkMessageBox.askquestion("Stopper la simulation? ", "Are You Sure? ?", icon='warning')
	if result == 'yes':
		if(h != None):
			h.stopSimulaion()
		if(myTread != None):
			myTread._Thread__stop()	
		if(stopW==True):
			mainWindow.destroy()
	
	
def saveSimulation():
	print("---saveSimulation ")
	global h
	opts = {}
	if(choice==1):
		print("----NOT IMPLEMENTED----")
		return
	if(choice==0):
		opts['filetypes'] = [('RL files', '*.rl')]
	elif(choice==1):
		opts['filetypes'] = [('HRL files', '*.hrl')]
	else:
		opts['filetypes'] = [("All files", "*.*")]
	
	opts['initialdir'] = './'
	opts['title'] = "Sauvegarder la simulation"	
	path= tkFileDialog.asksaveasfilename(**opts)
	if(not path):return
	output = open(path, "wb")
	dico = h.saveInstance()
	pickle.dump(dico, output)
	output.close()	
	print("---Simulation saved")
	
def stopAndSave():
	stopSimulation(False)
	saveSimulation()
	mainWindow.destroy()
	
	
def on_closing():
	global  myTread
	global h
	if tkMessageBox.askokcancel("Quit", "Do you want to quit?"):
		if(h != None):
			h.stopSimulaion()
		if(myTread != None):
			myTread._Thread__stop()	
		mainWindow.destroy()
			


if __name__ == '__main__':
	rospy.init_node('deplacement_case', anonymous=True)
	try:
		choice = -1
		global  mainWindow
		global  myTread
		global  h
		h = None
		myTread = None
		mainWindow = Tk()
		mainWindow.title("Projet IAR")	
		Button(mainWindow, text="Lancer une nouvelle simulation", command=createWindowNewSim).pack()
		Button(mainWindow, text="Charger une simulation", command=loadSimulation).pack()
		mainWindow.protocol("WM_DELETE_WINDOW", on_closing)
		mainWindow.mainloop()
	except rospy.ROSInterruptException: pass