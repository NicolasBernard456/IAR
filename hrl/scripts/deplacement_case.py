#!/usr/bin/env python

import rospy
from std_msgs.msg import Int16,Float32,Bool,Float32MultiArray,Int16MultiArray
from nav_msgs.msg import Odometry
from fastsim.srv import *




class Deplacement():
    def __init__(self):
        global x
        global y 
        self.x = 0.0
        self.y = 0.0
   
   
   #-------------------------------------------
    def callback_module(n, data):
        channel[n]=data
        #rospy.loginfo(rospy.get_caller_id()+" n=%d Activated: %d speed_l: %f speed_r: %f",n,data.activated, data.speed_left, data.speed_right)
    
    
    #-------------------------------------------
    def callback_odom(data):
      global odom
      odom=data
      
    def callback_next_pose(self,data):
        if(len(data.data) == 2):    #Envoi de coordonnee x y pixels
            self.x = data.data[0]
            self.y = data.data[1]
        elif(len(data.data) == 3):#Envoi de coordonnee x y normalise
            print('ok')
            self.x = 32 + data.data[1] * 60 + 3 * data.data[1] 
            self.y = 32 + data.data[2] * 60 + 3 * data.data[2]
        print(len(data.data))
    def deplacement(self):
        th = 0
        # Main loop:
        while (not rospy.is_shutdown()):
            if ((self.x > 0.0) & (self.x < 720.0) & (self.y > 0.0) & (self.y < 720.0)):
                rospy.wait_for_service('simu_fastsim/teleport')
                try:
                    # teleport robot
                    teleport = rospy.ServiceProxy('simu_fastsim/teleport', Teleport)
                    resp1 = teleport(self.x, self.y, th)
                    self.x = 0.0
                    self.y = 0.0
                except rospy.ServiceException, e:
                    print "Service call failed: %s"%e

#-------------------------------------------
if __name__ == '__main__':
    D = Deplacement()
    rospy.Subscriber("/next_pose", Float32MultiArray, D.callback_next_pose,0)

    rospy.init_node('deplacement_case', anonymous=True)
    try:
        D.deplacement()
    except rospy.ROSInterruptException: pass
