#!/usr/bin/env python

import rospy
from std_msgs.msg import Int16,Float32,Bool,Float32MultiArray,Int16MultiArray
from nav_msgs.msg import Odometry
from hrl.srv import deplacement_normalisee
from hrl.srv import fake_deplacement_normalisee
import numpy as np
import time
odom = Odometry()
class Hrl():
    def __init__(self):
        global x
        global y 
        self.x = 0.0
        self.y = 0.0
        self.tau = 10
        self.alphaC = 0.2
        self.alphaA = 0.1
        self.gamma = 0.9
        self.state = '' #Etat dans lequel se trouve le robot
        self.last_state = '' #Precedent etat dans lequel se trouvait le robot
        self.W = {} #Matrice des strengths
        self.send_data_W = Float32MultiArray()
        self.action = 1 #Action a effectuer
        self.reward = 0 #Reward pour l'action effectuee
        self.V = {}
        self.bool_slow = False #placer a true pour ralentir la simu
        self.affichage = False
        self.pub = rospy.Publisher("/Wsended", Float32MultiArray, queue_size = 10)
    #-------------------------------------------
    def callback_odom(self, data):
      #Mise a jour position robot
      global odom
      odom=data
      self.x = odom.pose.pose.position.x
      self.y = odom.pose.pose.position.y
      
    def discreteProb(self,p):
        # Draw a random number using probability table p (column vector)
        # Suppose probabilities p=[p(1) ... p(n)] for the values [1:n] are given, sum(p)=1 and the components p(j) are nonnegative. To generate a random sample of size m from this distribution imagine that the interval (0,1) is divided into intervals with the lengths p(1),...,p(n). Generate a uniform number rand, if this number falls in the jth interval give the discrete distribution the value j. Repeat m times.
        r = np.random.random()
        cumprob=np.hstack((np.zeros(1),p.cumsum()))
        sample = -1
        for j in range(p.size):
            if (r>cumprob[j]) & (r<=cumprob[j+1]):
                sample = j
                break
        return sample
      
      
#    def discreteProb(self,p):
#        actions = []
#        for i in range(8):
#            actions.insert(i ,i)
#        return np.random.choice(actions,1,list(p))[0] 
      
    def send_W(self):
        self.send_data_W = Float32MultiArray()
        print(len(self.W))        
        for i in range(11):
            for j in range(11):
                max = 0.0
                id = -1
                for k in range(8):
                    if not((str(float(i)) + ' ' + str(float(j)) + str(k)) in self.W.keys()):
                        self.W[str(float(i)) + ' ' + str(float(j)) + str(k)] = 0.0
                    if max < self.W[str(float(i)) + ' ' + str(float(j)) + str(k)]:
                        max = self.W[str(float(i)) + ' ' + str(float(j)) + str(k)]
                        id = k
                self.send_data_W.data.insert(i+j*11,id)
        self.pub.publish(self.send_data_W)
        print(len(self.W))
      
      
    
    def selection_action(self):
        tab_proba_action = np.zeros((8,1))
        somme_exp = 0        
        for i in range(8):
            somme_exp = somme_exp + np.exp(self.W[self.state+str(i)]/self.tau)
        for i in range(8):
            tab_proba_action[i] = np.exp(self.W[self.state+str(i)]/self.tau) / somme_exp
        self.action = self.discreteProb(tab_proba_action)
        
    
    def callback_vitesse_sim(self, data):
        self.bool_slow = data.data
    
    def callback_affichage_W(self,data):
        self.affichage = data.data
    
    
    def hrl_loop(self):
        #Odom permet de recuperer la position courante du robot
        rospy.Subscriber("/odom_normalisee", Odometry, self.callback_odom)
        rospy.Subscriber("/slow", Bool, self.callback_vitesse_sim)
        rospy.Subscriber("/affichage_W", Bool, self.callback_affichage_W)
        
        #Wait for service permet d'attendre que le service de deplacement du robot soit utilisable
        rospy.wait_for_service('deplacement_normalisee')
        rospy.wait_for_service('teleport_normalisee')
        rospy.wait_for_service('fake_deplacement_normalisee')
        #Boucle proncipale
        while (not rospy.is_shutdown()):
            try:
#                if self.last_state != '':
#                    self.last_state = self.state
#                else:
#                    self.last_state = str(self.x) + ' ' + str(self.y)
                if self.state == '':
                    self.state = str(self.x) + ' ' + str(self.y)
                    print('ok')
                self.last_state = self.state
#                print(len(self.V))
                for i in range(8):    
                    if not (self.state+str(i) in self.W.keys()) :
                        self.W[self.state+str(i)] = 0.0
                if not ( self.V.has_key(self.state)):                                  
#                    print('Nouvelle case')
                    self.V[self.state] = 0.0
#                print(self.V[self.state])
                self.selection_action() #selection de l'action



#                #faux deplacement
#                fake_deplacement = rospy.ServiceProxy('fake_deplacement_normalisee', fake_deplacement_normalisee)
#                tab = Float32MultiArray()    
#                tab.data = [self.action]           #Placer Ici la case vers laquelle se deplacer comme detaillee dans le readme
#                resp1 = fake_deplacement(tab)
#                self.reward = resp1.rew.data    
#                
                 # deplacement robot
                deplacement = rospy.ServiceProxy('deplacement_normalisee', fake_deplacement_normalisee)
                tab = Float32MultiArray()    
                tab.data = [self.action]           #Placer Ici la case vers laquelle se deplacer comme detaillee dans le readme
                resp1 = deplacement(tab)
                self.reward = resp1.rew.data
                self.state = str(resp1.new_pos.data[0]) + ' ' + str(resp1.new_pos.data[1])  #oon recupere les nouvelles positions x et y
                
                for i in range(8):    
                   if not (self.state+str(i) in self.W.keys()) :
                       self.W[self.state+str(i)] = 0.0
                if not (self.state in self.V.keys()):
                   self.V[self.state] = 0.0
                
#                if(self.reward != 0):
                delta = self.reward + self.gamma * self.V[self.state] - self.V[self.last_state]  #prediction error
                self.W[self.last_state+str(self.action)] = self.W[self.last_state+str(self.action)] + self.alphaA * delta
                self.V[self.last_state] = self.V[self.last_state] + self.alphaC * delta
#                print(self.V[self.last_state])
               
                if(self.reward == 100.0):
                    print('OK')
                    teleport = rospy.ServiceProxy('teleport_normalisee', deplacement_normalisee)
                    tab = Float32MultiArray()    
                    tab.data.insert(1,9)
                    tab.data.insert(2,1)                    
                    tp = teleport(tab)
                    self.state = str(tab.data[0]) + ' ' + str(tab.data[1])
                if(self.bool_slow):
                    time.sleep(0.5)                
                if(self.affichage):
                    self.send_W()
                    self.affichage = False
            except rospy.ServiceException, e:
                print "Service call failed: %s"%e

#-------------------------------------------
if __name__ == '__main__':
    h = Hrl()
    rospy.init_node('deplacement_case', anonymous=True)
    try:
        h.hrl_loop()
    except rospy.ROSInterruptException: pass
