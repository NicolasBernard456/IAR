#!/usr/bin/env python

import rospy
from std_msgs.msg import Int16,Float32,Bool,Float32MultiArray,Int16MultiArray
from nav_msgs.msg import Odometry
from hrl.srv import deplacement_normalisee
from hrl.srv import fake_deplacement_normalisee
import numpy as np
import time
import os
import tkFileDialog 
import tkMessageBox
odom = Odometry()
import matplotlib.pyplot as plt
class Hrl():
	def __init__(self):
		global x
		global y 
		self.stopSim = False
		self.x = 0.0
		self.y = 0.0
		self.tau = 10
		self.alphaC = 0.2
		self.alphaA = 0.1
		self.gamma = 0.9
		self.state = '' #Etat dans lequel se trouve le robot
		self.last_state = '' #Precedent etat dans lequel se trouvait le robot
		self.W = {} #Matrice des strengths
		split = os.environ.get('ROS_PACKAGE_PATH').split(":")
		self.catkinDir = ""
		for val in split:
			if "catkin_ws"  in val: 
				self.catkinDir = val
				break
		self.hrlDir = 	self.catkinDir+"/IAR/hrl/"
		self.dataDir = self.hrlDir+"/data"
		self.StartTime = rospy.get_time() 
		
		#Matrice des strenght pour les options
		self.W1to2 = np.load(self.dataDir+'/W1.npy').item()
		self.W1to3 = np.load(self.dataDir+'/W0.npy').item()
		self.W2to1 = np.load(self.dataDir+'/W2.npy').item()
		self.W2to4 = np.load(self.dataDir+'/W3.npy').item()
		self.W3to1 = np.load(self.dataDir+'/W4.npy').item()
		self.W3to4 = np.load(self.dataDir+'/W5.npy').item()
		self.W4to2 = np.load(self.dataDir+'/W6.npy').item()
		self.W4to3 = np.load(self.dataDir+'/W7.npy').item()
		self.W_option = {}
		self.send_data_W = Float32MultiArray()
		self.action = 1 #Action a effectuer
		self.reward = 0 #Reward pour l'action effectuee
		self.V = {}
		self.t_tot = 1
		self.pseudo_reward = ''#Permet d'indiquer la position de fin pour une option et donc de savoir quand terminer une option
		self.bool_slow = False #placer a true pour ralentir la simu
		self.affichage = False
		self.pub = rospy.Publisher("/Wsended", Float32MultiArray, queue_size = 10)
		self.pub_odom = rospy.Publisher("/simu_fastsim/odom", Odometry, queue_size = 10)
		self.iteration = 0
		self.nbPartie = 0
		self.nbPas = 0
		self.figure = None
		self.Xpoints = []
		self.YPoints = []
	#-------------------------------------------
	def updateGraph(self):
		print("--update---")
		
		self.Xpoints.append(self.nbPartie)
		self.YPoints.append(self.nbPas)
		plt.clf()  
		plt.ylabel("Steps")
		plt.xlabel("Episode")		
		plt.plot(self.Xpoints ,self.YPoints)
		self.figure.canvas.draw()
		
	def saveInstance(self):
		dico = {}
		#dico["stopSim"] = self.stopSim
		dico["x"] =  self.x
		dico["y"] =  self.y
		dico["state"] =  self.state
		dico["last_state"] =  self.last_state
		dico["W"] =  self.W
		dico["send_data_W"] =  self.send_data_W
		dico["action"] =  self.action
		dico["reward"] =  self.reward
		dico["V"] =  self.V
		dico["bool_slow"] =  self.bool_slow
		dico["affichage"] =  self.affichage
		dico["duringSimul"] = rospy.get_time() - self.StartTime
		
		dico["W_option"] =  self.W_option
		dico["t_tot"] =  self.t_tot
		dico["pseudo_reward"] =  self.pseudo_reward
		dico["iteration"] =  self.iteration	
		return dico
	
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

	def send_W(self,arg):
		self.send_data_W = Float32MultiArray()
		#print(len(arg))        
		for i in range(11):
			for j in range(11):
				max = 0.0
				id = -1
				for k in range(10):
					if not((str(float(i)) + ' ' + str(float(j)) + str(k)) in arg.keys()):
						arg[str(float(i)) + ' ' + str(float(j)) + str(k)] = 0.0
					if max < arg[str(float(i)) + ' ' + str(float(j)) + str(k)]:
						max = arg[str(float(i)) + ' ' + str(float(j)) + str(k)]
						id = k
				self.send_data_W.data.insert(j+i*11,id)
		self.pub.publish(self.send_data_W)
		#print(len(arg))



	def selection_action(self):
		tab_proba_action = np.zeros((10,1))
		somme_exp = 0        
		for i in range(10):
			somme_exp = somme_exp + np.exp(self.W[self.state+str(i)]/self.tau)
		for i in range(10):
			tab_proba_action[i] = np.exp(self.W[self.state+str(i)]/self.tau) / somme_exp
		self.action = self.discreteProb(tab_proba_action)

	def selection_action_option_prob(self):
		tab_proba_action = np.zeros((8,1))
		somme_exp = 0        
		for i in range(8):
			somme_exp = somme_exp + np.exp(self.W_option[self.state+str(i)]/self.tau)
		for i in range(8):
			tab_proba_action[i] = np.exp(self.W_option[self.state+str(i)]/self.tau) / somme_exp
		self.action = self.discreteProb(tab_proba_action)

	def selection_action_option_determinist(self):
		max = 0
		id = -1
		for i in range(8):
			if max < self.W_option[self.state+str(i)]:
				max = self.W_option[self.state+str(i)]
				id = i

		if(id != -1):
			self.action = id
		else:
			self.selection_action_option_prob()
#        print self.action
        
        
    
	def callback_vitesse_sim(self, data):
		self.bool_slow = data.data
    
	def callback_affichage_W(self,data):
		self.affichage = data.data
		np.save(self.dataDir+'/W_hrl.npy', self.W)
		print rospy.get_time() - self.StartTime
        
	def stopSimulaion(self):
		print("stopSimulaion")
		self.stopSim = True
		
	def set_W_option(self):
		self.W_option = {}
		#if((self.action%2) == 0):
		#print 'action1'
		#else:
		#print 'action2'
		if((self.x < 5.0) & (self.y < 5.0)): #Robot place dans la salle superieur gauche
			if((self.action%2) == 0):
				self.W_option = self.W1to2	
				self.pseudo_reward = str(5.0) + ' ' + str(2.0)#Le goal est set a la position 5 2 (case du haut)
			else:
				self.W_option = self.W1to3
				self.pseudo_reward = str(1.0) + ' ' + str(5.0)#Le goal est set a la position 1 5.0 (case de gauche)
		elif((self.x > 5.0) & (self.y < 6.0)):         #Robot place dans la salle superieur droite
			if((self.action%2) == 0):
				self.W_option = self.W2to1
				self.pseudo_reward = str(5.0) + ' ' + str(2.0)#Le goal est set a la position 5 2 (case du haut)
			else:
				self.W_option = self.W2to4
				self.pseudo_reward = str(8.0) + ' ' + str(6.0)#Le goal est set a la position 8 6 (case de droite)
		elif((self.x < 5.0) & (self.y > 5.0)):        #Robot place dans le coin inferieur gauche
			if((self.action%2) == 0):
				self.W_option = self.W3to1
				self.pseudo_reward = str(1.0) + ' ' + str(5.0)#Le goal est set a la position 1 5.0 (case de gauche)
			else:
				self.W_option = self.W3to4
				self.pseudo_reward = str(5.0) + ' ' + str(9.0)#Le goal est set a la position 5 9 (case du bas)
		elif((self.x > 5.0) & (self.y > 6.0) ):        #Robot place dans le coin inferieur droit
			if((self.action%2) == 0):
				self.W_option = self.W4to2
				self.pseudo_reward = str(8.0) + ' ' + str(6.0)#Le goal est set a la position 8 6 (case de droite)
			else:
				self.W_option = self.W4to3
				self.pseudo_reward = str(5.0) + ' ' + str(9.0)#Le goal est set a la position 5 9 (case du bas)
		elif((self.x == 1.0) & (self.y == 5.0)):     #Robot place sur la case seul de gauche
			if((self.action%2) == 0):
				self.W_option = self.W1to2
				self.pseudo_reward = str(5.0) + ' ' + str(2.0)#Le goal est set a la position 5 2 (case du haut)
			else:
				self.W_option = self.W3to4
				self.pseudo_reward = str(5.0) + ' ' + str(9.0)#Le goal est set a la position 5 9 (case du bas)
		elif((self.x == 5.0) & (self.y == 2.0)):     #Robot place sur la case seul du haut
			if((self.action%2) == 0):
				self.W_option = self.W1to3
				self.pseudo_reward = str(1.0) + ' ' + str(5.0)#Le goal est set a la position 1 5.0 (case de gauche)
			else:
				self.W_option = self.W2to4
				self.pseudo_reward = str(8.0) + ' ' + str(6.0)#Le goal est set a la position 8 6 (case de droite)
		elif((self.x == 5.0) & (self.y == 9.0)):     #Robot place sur la case seul du bas
			if((self.action%2) == 0):
				self.W_option = self.W3to1
				self.pseudo_reward = str(1.0) + ' ' + str(5.0)#Le goal est set a la position 1 5.0 (case de gauche)
			else:
				self.W_option = self.W4to2
				self.pseudo_reward = str(8.0) + ' ' + str(6.0)#Le goal est set a la position 8 6 (case de droite)
		elif((self.x == 8.0) & (self.y == 6.0)):     #Robot place sur la case seul de droite
			if((self.action%2) == 0):
				self.W_option = self.W2to1
				self.pseudo_reward = str(5.0) + ' ' + str(2.0)#Le goal est set a la position 5 2 (case du haut)
			else:
				self.W_option = self.W4to3    
				self.pseudo_reward = str(5.0) + ' ' + str(9.0) #Le goal est set a la position 5 9 (case du bas)

                
	def do_option(self):   
		self.set_W_option()
		#print('Execution option : going to ' + str(self.pseudo_reward))   
		stop = False
		self.t_tot = 1
		saver_action = self.action					#On enregistre la derniere action pour la recuperer a la fin de loption
		while ((not rospy.is_shutdown()) & (stop == False)):
			for i in range(8):    					#Reinit des W si necessaire
				if not (self.state+str(i) in self.W_option.keys()) :
					self.W_option[self.state+str(i)] = 0.0
			#self.selection_action_option_prob() #selection de l'action probabiliste
			self.selection_action_option_determinist() #selection de l'action deterministe
				
			time.sleep(0.075)
			# deplacement robot
			deplacement = rospy.ServiceProxy('deplacement_normalisee', fake_deplacement_normalisee)
			tab = Float32MultiArray()    
			tab.data = [self.action]           				#Placer Ici la case vers laquelle se deplacer comme detaillee dans le readme
			resp1 = deplacement(tab)
			self.state = str(resp1.new_pos.data[0]) + ' ' + str(resp1.new_pos.data[1])  #on recupere les nouvelles positions x et y
			self.t_tot = self.t_tot + 1
			self.x = resp1.new_pos.data[0]
			self.y = resp1.new_pos.data[1]
			
			self.nbPas = self.nbPas + 1	 
			
			self.iteration = self.iteration + 1
			#print ("iteration : "+str(self.iteration))
			
			if(self.state == self.pseudo_reward):			#Si on atteint la position darrivee
				stop = True
				self.action = saver_action 				#On reprend la derniere action selectionne
			#print 'Ending option arrived at' + str(self.state)
			
			#if(self.affichage):
			#self.send_W(self.W_option)
			#self.affichage = False
		#            print 'executing option'
        
	def hrl_loop(self):
		rospy.Subscriber("/slow", Bool, self.callback_vitesse_sim)	  #Permet de ralentir la simu        
		rospy.Subscriber("/affichage_W", Bool, self.callback_affichage_W) #Permet d afficher W 
		
		#Wait for service permet d'attendre que le service de deplacement du robot soit utilisable
		rospy.wait_for_service('deplacement_normalisee')
		rospy.wait_for_service('teleport_normalisee')
		rospy.wait_for_service('fake_deplacement_normalisee')
		#Boucle proncipale
		self.iteration = 0		
		while (not rospy.is_shutdown() | ( self.stopSim)):
			try:
				self.nbPas = self.nbPas + 1	
				self.iteration = self.iteration + 1 			#On compte les iterations
				self.reward = 0.0					#Initialisation reward
				if self.state == '':					#Initialisation state
					self.state = str(self.x) + ' ' + str(self.y)
					#print('ok')
				self.last_state = self.state				#Initialisation last state
				for i in range(10):    					#Initialisation des W(state + action)
					if not (self.state+str(i) in self.W.keys()) :
						self.W[self.state+str(i)] = 0.0
				#                        print(self.state)
				#                print(self.state)
				if not ( self.V.has_key(self.state)):                   #Initialisation de V(state)   
					#print('Nouvelle case')
					self.V[self.state] = 0.0
		#                print(self.V[self.state])
				self.selection_action() 				#selection de l'action
				if(self.action >= 8):					#Si on a choisit une option on rentre dans une boucle specifique
					self.do_option()
				else:						
					#Sinon on execute l'action simple
					# deplacement robot
					deplacement = rospy.ServiceProxy('deplacement_normalisee', fake_deplacement_normalisee)
					tab = Float32MultiArray()    
					tab.data = [self.action]           			#Placer Ici la case vers laquelle se deplacer comme detaillee dans le readme
					resp1 = deplacement(tab)
					self.reward = resp1.rew.data			#Recuperation de la reward
					self.state = str(resp1.new_pos.data[0]) + ' ' + str(resp1.new_pos.data[1])  #on recupere les nouvelles positions x et y
					self.x = resp1.new_pos.data[0]
					self.y = resp1.new_pos.data[1]                    
					self.t_tot = 1

				for i in range(10):    					#Initialisation des W(state + action)
					if not (self.state+str(i) in self.W.keys()) :
						self.W[self.state+str(i)] = 0.0
				if not (self.state in self.V.keys()):			#Initialisation de V(state)  
					self.V[self.state] = 0.0

				#Calcul de delta
				delta = self.reward + np.power(self.gamma,self.t_tot) * self.V[self.state] - self.V[self.last_state]  #prediction error
				#Mise a jour de W et V
				self.W[self.last_state+str(self.action)] = self.W[self.last_state+str(self.action)] + self.alphaA * delta
				self.V[self.last_state] = self.V[self.last_state] + self.alphaC * delta


				if(self.reward == 100.0):				#Si on atteint la reward
					print('reward')
					self.updateGraph()
					self.nbPartie = self.nbPartie +1
					self.nbPas = 0
					teleport = rospy.ServiceProxy('teleport_normalisee', deplacement_normalisee)
					tab = Float32MultiArray()    
					tab.data.insert(1,9)
					tab.data.insert(2,1)
					odom.pose.pose.position.x = 32 + 9 * 63
					odom.pose.pose.position.y = 32 + 1 * 63
					self.pub_odom.publish(odom)
					tp = teleport(tab)					#Teleport du robot a sa position de depart
					self.x = 9
					self.y = 1
					#                    self.state = str(tab.data[0]) + ' ' + str(tab.data[1])
				if(self.bool_slow):					
					time.sleep(1.0)
				time.sleep(0.075)
				if(self.affichage):
					self.send_W(self.W)
					self.affichage = False

				
				seconds = rospy.get_time() - self.StartTime
				m, s = divmod(seconds, 60)
				h, m = divmod(m, 60)
				#print "%d:%02d:%02d" % (h, m, s)
				#print ("iteration : "+str(self.iteration))
			except rospy.ServiceException, e:
				print "Service call failed: %s"%e
			
			
		np.save(self.dataDir+'/W_hrl.npy', self.W)

#-------------------------------------------
if __name__ == '__main__':
	rospy.init_node('deplacement_case', anonymous=True)
	h = Hrl()
	try:
		h.hrl_loop()
	except rospy.ROSInterruptException: pass

def createHRL(dico):
	instance = Hrl()
	#instance.stopSim = dico["stopSim"] 
	instance.x = dico["x"]
	instance.y = dico["y"]
	instance.state = dico["state"]
	instance.last_state = dico["last_state"] 
	instance.W = dico["W"]
	instance.send_data_W = dico["send_data_W"]
	instance.action = dico["action"] 
	instance.reward = dico["reward"]
	instance.V = dico["V"]
	instance.bool_slow = dico["bool_slow"] 
	instance.affichage = dico["affichage"]

	instance .W_option =  dico["W_option"] 
	instance.t_tot = dico["t_tot"]
	instance.pseudo_reward = dico["pseudo_reward"]
	instance.iteration = dico["iteration"]	
	instance.StartTime = rospy.get_time() - dico["duringSimul"]
	#self.StartTime = rospy.get_time() 
	
	# On teleport le robot la ou il etait avant
	teleport = rospy.ServiceProxy('teleport_normalisee', deplacement_normalisee)
	tab = Float32MultiArray()
	xPos = instance.x
	yPos = instance.y
	tab.data.insert(1,xPos)
	tab.data.insert(2,yPos)
	odom.pose.pose.position.x = 32 + xPos * 63
	odom.pose.pose.position.y = 32 + yPos * 63
	instance.pub_odom.publish(odom)
	tp = teleport(tab)
	
	
	return instance	