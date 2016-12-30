#!/usr/bin/env python

import rospy
from std_msgs.msg import Int16,Float32,Bool,Float32MultiArray,Int16MultiArray
from nav_msgs.msg import Odometry
from hrl.srv import deplacement_normalisee
import numpy as np
import time
odom = Odometry()
class Hrl():
    def __init__(self):
        global x
        global y 
        self.x = 0.0
        self.y = 0.0
        self.alpha = 1.0
        self.tau = 10
        self.alphaC = 0.2
        self.alphaA = 0.1
        self.gamma = 0.9
        self.state = '' #Etat dans lequel se trouve le robot
        self.last_state = '' #Precedent etat dans lequel se trouvait le robot
        self.W = {} #Matrice des strengths
        self.action = 1 #Action a effectuer
        self.reward = 0 #Reward pour l'action effectuee
        self.V = {}
        self.bool_slow = False #placer a true pour ralentir la simu
    #-------------------------------------------
    def callback_odom(self, data):
      #Mise a jour position robot
      global odom
      odom=data
      self.x = odom.pose.pose.position.x
      self.y = odom.pose.pose.position.y
      
#    def discreteProb(self,p):
#        # Draw a random number using probability table p (column vector)
#        # Suppose probabilities p=[p(1) ... p(n)] for the values [1:n] are given, sum(p)=1 and the components p(j) are nonnegative. To generate a random sample of size m from this distribution imagine that the interval (0,1) is divided into intervals with the lengths p(1),...,p(n). Generate a uniform number rand, if this number falls in the jth interval give the discrete distribution the value j. Repeat m times.
#        r = np.random.random()
#        cumsum = 0
#        for i in range(len(p)):
#            cumsum = cumsum + p[i]
#        cumprob=np.hstack((np.zeros(1),cumsum))
#        sample = -1
#        for j in range(len(p)):
#            if (r>cumprob[j]) & (r<=cumprob[j+1]):
#                sample = j
#                break
#        return sample
      
      
    def discreteProb(self,p):
        actions = []
        for i in range(7):
            actions.insert(i ,i)
        return np.random.choice(actions,1,list(p))[0] 
    
    def selection_action(self):
        tab_proba_action = []
        somme_exp = 0        
        for i in range(8):
            somme_exp = somme_exp + np.exp(self.W[self.state+str(i)]/self.tau)
        for i in range(8):
            tab_proba_action.insert(i, np.exp(self.W[self.state+str(i)]/self.tau) / somme_exp)
        self.action = self.discreteProb(tab_proba_action)
        
    
    def callback_vitesse_sim(self, data):
        self.bool_slow = data.data
    
    def hrl_loop(self):
        #Odom permet de recuperer la position courante du robot
        rospy.Subscriber("/odom_normalisee", Odometry, self.callback_odom)
        rospy.Subscriber("/slow", Bool, self.callback_vitesse_sim)
        #Wait for service permet d'attendre que le service de deplacement du robot soit utilisable
        rospy.wait_for_service('deplacement_normalisee')
        rospy.wait_for_service('teleport_normalisee')
        
        #Boucle proncipale
        while (not rospy.is_shutdown()):
            try:
                if self.last_state != '':
                    self.last_state = self.state
                else:
                    self.last_state = str(self.x) + ' ' + str(self.y)
                
                self.state = str(self.x) + ' ' + str(self.y)
                for i in range(8):    
                    if not (self.state+str(i) in self.W.keys()) :
                        self.W[self.state+str(i)] = 0

                self.selection_action() #selection de l'action
                
                if not (self.state in self.V.keys()):
                    self.V[self.state] = 0
                    
                    
                    
                
                delta = self.reward + self.gamma * self.V[self.state] - self.V[self.last_state]  #prediction error
                
                
                self.V[self.last_state] = self.V[self.last_state] + self.alphaC * delta
                self.W[self.state+str(self.action)] = self.W[self.state+str(self.action)] + self.alphaA * delta
                
                # deplacement robot
                deplacement = rospy.ServiceProxy('deplacement_normalisee', deplacement_normalisee)
                tab = Float32MultiArray()    
                tab.data = [self.action]           #Placer Ici la case vers laquelle se deplacer comme detaillee dans le readme
                resp1 = deplacement(tab)
                self.reward = resp1.rew.data
                if(self.reward == 1):
                    print('OK')
                    teleport = rospy.ServiceProxy('teleport_normalisee', deplacement_normalisee)
                    tab = Float32MultiArray()    
                    tab.data.insert(1,9)
                    tab.data.insert(2,1)                    
                    tp = teleport(tab)
                if(self.bool_slow):
                    time.sleep(0.5)
            except rospy.ServiceException, e:
                print "Service call failed: %s"%e

#-------------------------------------------
if __name__ == '__main__':
    h = Hrl()
    rospy.init_node('deplacement_case', anonymous=True)
    try:
        h.hrl_loop()
    except rospy.ROSInterruptException: pass
