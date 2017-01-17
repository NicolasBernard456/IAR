#!/usr/bin/env python

import rospy
from std_msgs.msg import Int16,Float32,Bool,Float32MultiArray,Int16MultiArray
from nav_msgs.msg import Odometry
from hrl.srv import deplacement_normalisee
from hrl.srv import fake_deplacement_normalisee
import numpy as np
import time
odom = Odometry()
class option_learning():
    def __init__(self):
        global x
        global y 
        self.x = 0.0
        self.y = 0.0
        self.min_x = 0.0
        self.min_y = 0.0
        self.max_x = 0.0
        self.max_y = 0.0
        self.tau = 10
        self.alphaC = 0.1
        self.alphaA = 0.01
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
        self.cpt_option = 0
        self.cpt_action = 0
        self.last_cpt_action = self.cpt_action
        self.min_cpt_action = 1000
        self.stop = False
        self.pub = rospy.Publisher("/Wsended", Float32MultiArray, queue_size = 10)
        self.pub_odom = rospy.Publisher("/simu_fastsim/odom", Odometry, queue_size = 10)
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
                self.send_data_W.data.insert(j+i*11,id)
        self.pub.publish(self.send_data_W)
        print(len(self.W))
      
      
    
    def selection_action(self):
        tab_proba_action = np.zeros((8,1))
        
        wrong_state = False
#        while(wrong_state == False):
        somme_exp = 0
#            wrong_state = True
        for i in range(8):
            somme_exp = somme_exp + np.exp(self.W[self.state+str(i)]/self.tau)
            
        for i in range(8):
            tab_proba_action[i] = np.exp(self.W[self.state+str(i)]/self.tau) / somme_exp            
#                if(tab_proba_action[i] == 1.0):
#                    wrong_state = False
#            if(wrong_state == False):
#                for i in range(8):
#                    self.W[self.state+str(i)] = 0.0
#                    print 'Reset W'
        self.action = self.discreteProb(tab_proba_action)
#        print self.action
#        print tab_proba_action
        
    
    def callback_vitesse_sim(self, data):
        self.bool_slow = data.data
    
    def callback_affichage_W(self,data):
        self.affichage = data.data
    
    def load_dic(self,name_file):
        self.W = np.load('catkin_ws/src/IAR/hrl/data/' + name_file + '.npy').item()
        
    
    
    def save_dic(self,name_file):
        np.save('catkin_ws/src/IAR/hrl/data/' + name_file + '.npy', self.W)
        self.W = {}
        self.V = {}
        self.state = '' #Etat dans lequel se trouve le robot
        self.last_state = '' #Precedent etat dans lequel se trouvait le robot
        self.cpt_option = 0
        self.cpt_action = 0
        self.min_cpt_action = 1000
        self.stop = False
    
    def option_learning_loop(self,posx_depart_origine,posy_depart_origine,posx_arrive,posy_arrive,sizex,sizey,posx_final,posy_final):
        #Odom permet de recuperer la position courante du robot
#        rospy.Subscriber("/odom_normalisee", Odometry, self.callback_odom)
        rospy.Subscriber("/slow", Bool, self.callback_vitesse_sim)
        rospy.Subscriber("/affichage_W", Bool, self.callback_affichage_W)
        
        #Wait for service permet d'attendre que le service de deplacement du robot soit utilisable
        
        rospy.wait_for_service('deplacement_normalisee')
        rospy.wait_for_service('teleport_normalisee')
        rospy.wait_for_service('fake_deplacement_normalisee')
        
        startT = rospy.get_time()       
        #Teleporte le robot vers sa position initiale
        self.max_x = posx_depart_origine + sizex
        self.min_x = posx_depart_origine
        self.min_y = posy_depart_origine
        self.max_y = posy_depart_origine + sizey
        posx_depart = posx_depart_origine - 1     
        posy_depart = posy_depart_origine - 1
        
        for kx in range(sizex):
            posx_depart = posx_depart + 1
            posy_depart = posy_depart_origine - 1
            for ky in range(sizey + 1):
                
                posy_depart = posy_depart + 1
                if((ky == sizey) & (kx == sizex - 1)):
                    posx_depart = posx_final
                    posy_depart = posy_final
                elif(ky == sizey):
                    continue

                self.V = {}
                self.state = '' #Etat dans lequel se trouve le robot
                self.last_state = '' #Precedent etat dans lequel se trouvait le robot
                self.cpt_option = 0
                self.cpt_action = 0
                self.min_cpt_action = 1000
                self.stop = False
                teleport = rospy.ServiceProxy('teleport_normalisee', deplacement_normalisee)
                tab = Float32MultiArray()    
                tab.data.insert(1,posx_depart)
                tab.data.insert(2,posy_depart)
                odom.pose.pose.position.x = 32 + posx_depart * 63
                odom.pose.pose.position.y = 32 + posy_depart * 63
                self.x = posx_depart
                self.y = posy_depart
                self.pub_odom.publish(odom)
                tp = teleport(tab)
                time.sleep(0.075)
                #Boucle principale
                
                while ((not rospy.is_shutdown()) & (self.stop == False)):
                    try:
                        self.cpt_action  = self.cpt_action + 1
                        self.reward = 0.0
                        if self.state == '':
                            self.state = str(self.x) + ' ' + str(self.y)
                            print('ok')
                        self.last_state = self.state
                        for i in range(8):    
                            if not (self.state+str(i) in self.W.keys()) :
                                self.W[self.state+str(i)] = 0.0
                        if not ( self.V.has_key(self.state)):
                            self.V[self.state] = 0.0
                        count_blocage = 0
                        while(True):
                            count_blocage = count_blocage + 1
                            self.selection_action() #selection de l'action
                            
                            time.sleep(0.075)
                             #fake deplacement robot
                            fake_deplacement = rospy.ServiceProxy('fake_deplacement_normalisee', fake_deplacement_normalisee)
                            tab = Float32MultiArray()    
                            tab.data = [self.action]           #Placer Ici la case vers laquelle se deplacer comme detaillee dans le readme
                            resp1 = fake_deplacement(tab)
                            if((resp1.new_pos.data[0] == posx_arrive) & (resp1.new_pos.data[1] == posy_arrive)):                  
                                self.reward = 100
                            else:
                                self.reward = 0
                            self.x = resp1.new_pos.data[0]                            
                            self.y = resp1.new_pos.data[1]
#                            print self.x                            
#                            print self.y
                            
                            if(not ((self.x < self.min_x) | (self.x > self.max_x) | (self.y < self.min_y) | (self.y > self.max_y))):
                                break
                            elif(self.reward == 100):
                                break
                            else:
                                print 'coince'
                            print count_blocage
                            if(count_blocage > 100):
                                for i in range(8):
                                    self.W[self.state+str(i)] = 0.0
                                    print 'Reset W'
        #                print self.x
        #                print self.y
                            
                        deplacement = rospy.ServiceProxy('deplacement_normalisee', fake_deplacement_normalisee)
                        tab = Float32MultiArray()    
                        tab.data = [self.action]           #Placer Ici la case vers laquelle se deplacer comme detaillee dans le readme
                        resp1 = deplacement(tab)
                        if((resp1.new_pos.data[0] == posx_arrive) & (resp1.new_pos.data[1] == posy_arrive)):                  
                            self.reward = 100
                        else:
                            self.reward = 0
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
        #                if(self.W[self.last_state+str(self.action)] != 0):                    
        #                    print('changed')
        #                    print(self.last_state)
        #                    print(self.action)
        #                    self.bool_slow = True
                       
                        if(self.reward == 100.0):
                            print('OK')
                            teleport = rospy.ServiceProxy('teleport_normalisee', deplacement_normalisee)
                            tab = Float32MultiArray()    
                            tab.data.insert(1,posx_depart)
                            tab.data.insert(2,posy_depart)
                            odom.pose.pose.position.x = 32 + posx_depart * 63
                            odom.pose.pose.position.y = 32 + posy_depart * 63
                            self.pub_odom.publish(odom)    
                            time.sleep(0.075)                            
                            tp = teleport(tab)
                            if(self.cpt_action - self.min_cpt_action <= 3):
                               self.cpt_option = self.cpt_option + 1
                            elif(self.last_cpt_action == self.cpt_action):
                                self.cpt_option = self.cpt_option + 1
                            else:
                                self.cpt_option = 0
                                
                            if(self.cpt_action < self.min_cpt_action):
                                self.min_cpt_action = self.cpt_action
                                self.cpt_option = 0
                            
                            if(self.cpt_option > 30): #Si on reussit a atteindre l arrivee 30 fois on considere que l'agent a appris
                                self.stop = True
                                print str(rospy.get_time() - startT)
                            print self.cpt_option
                            print self.min_cpt_action
                            print self.cpt_action
                            self.last_cpt_action = self.cpt_action
                            self.cpt_action = 0
                        if(self.bool_slow):
                            time.sleep(1.0)
                        time.sleep(0.075)
                        if(self.affichage):
                            self.send_W()
                            self.affichage = False
                    except rospy.ServiceException, e:
                        print "Service call failed: %s"%e

#-------------------------------------------
if __name__ == '__main__':
    posx_depart = [0.0, 0.0, 6.0, 6.0, 0.0, 0.0, 6.0, 6.0]
    posy_depart = [0.0, 0.0, 0.0, 0.0, 6.0, 6.0, 7.0, 7.0]
    sizex = 5
    sizey = [5, 5, 6, 6, 5, 5, 4, 4]
    posx_arrive = [1.0, 5.0, 5.0, 8.0, 1.0, 5.0, 8.0, 5.0]
    posy_arrive = [5.0, 2.0, 2.0, 6.0, 5.0, 9.0, 6.0, 9.0]
         
    h = option_learning()
    rospy.init_node('option_learning', anonymous=True)
    
    startTime = rospy.get_time()  
    try:
        for i in range(0,8):
            h.load_dic('W' + str(i))
            if(i%2 == 0):
                h.option_learning_loop(posx_depart[i],posy_depart[i],posx_arrive[i],posy_arrive[i],sizex,sizey[i],posx_arrive[i+1],posy_arrive[i+1])            
            else:
                h.option_learning_loop(posx_depart[i],posy_depart[i],posx_arrive[i],posy_arrive[i],sizex,sizey[i],posx_arrive[i-1],posy_arrive[i-1])            
#            if(i%2 == 0):
#                h.option_learning_loop(posx_depart[i],posy_depart[i],posx_arrive[i],posy_arrive[i],1,1,posx_arrive[i+1],posy_arrive[i+1])            
#            else:
#                h.option_learning_loop(posx_depart[i],posy_depart[i],posx_arrive[i],posy_arrive[i],1,1,posx_arrive[i-1],posy_arrive[i-1])            

            h.save_dic('W' + str(i))
        print rospy.get_time() - startTime
    except rospy.ROSInterruptException: pass
    