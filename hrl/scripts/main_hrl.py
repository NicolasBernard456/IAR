#!/usr/bin/env python

import rospy
from std_msgs.msg import Int16,Float32,Bool,Float32MultiArray,Int16MultiArray
from nav_msgs.msg import Odometry
from hrl.srv import deplacement_normalisee


odom = Odometry()
class Deplacement():
    def __init__(self):
        global x
        global y 
        self.x = 0.0
        self.y = 0.0
    
    #-------------------------------------------
    def callback_odom(self, data):
      #Mise a jour position robot
      global odom
      odom=data
      self.x = odom.pose.pose.position.x
      self.y = odom.pose.pose.position.y
      
    def deplacement(self):
        #Odom permet de recuperer la position courante du robot
        rospy.Subscriber("/odom_normalisee", Odometry, self.callback_odom)
        #Wait for service permet d'attendre que le service de deplacement du robot soit utilisable
        rospy.wait_for_service('deplacement_normalisee')
        
        #Boucle proncipale
        while (not rospy.is_shutdown()):
            try:
                # deplacement robot
                deplacement = rospy.ServiceProxy('deplacement_normalisee', deplacement_normalisee)
                tab = Float32MultiArray()
                tab.data = [6]           #Placer Ici la case vers laquelle se déplcer comme detaillee dans le readme
                resp1 = deplacement(tab)



            except rospy.ServiceException, e:
                print "Service call failed: %s"%e

#-------------------------------------------
if __name__ == '__main__':
    D = Deplacement()
    rospy.init_node('deplacement_case', anonymous=True)
    try:
        D.deplacement()
    except rospy.ROSInterruptException: pass
