#!/usr/bin/env python

import rospy
from std_msgs.msg import Int16,Float32,Bool,Float32MultiArray,Int16MultiArray
from nav_msgs.msg import Odometry
from hrl.srv import deplacement_normalisee
from hrl.srv import fake_deplacement_normalisee
import numpy as np
import time
odom = Odometry()
from Tkinter import *


if __name__ == '__main__':
	#h = Hrl()
	rospy.init_node('deplacement_case', anonymous=True)
	try:
		fenetre = Tk()
		champ_label = Label(fenetre, text="Salut les Zeros !") 
		champ_label.pack()
		fenetre.mainloop()

		#h.hrl_loop()
	except rospy.ROSInterruptException: pass