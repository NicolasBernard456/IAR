#!/usr/bin/env python

import rospy
from std_msgs.msg import Int16,Float32,Bool,Float32MultiArray,Int16MultiArray
from nav_msgs.msg import Odometry
from hrl.srv import deplacement_normalisee
from hrl.srv import fake_deplacement_normalisee
import numpy as np
import time
odom = Odometry()
class Rl():
	def __init__(self):
		global x
		global y
		self.stopSim = False
		self.x = 0
		self.y = 0
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
		self.pub_odom = rospy.Publisher("/simu_fastsim/odom", Odometry, queue_size = 10)
	#-------------------------------------------
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
		#dico[""] =  self.pub = rospy.Publisher("/Wsended", Float32MultiArray, queue_size = 10)
		#dico[""] =  self.pub_odom = rospy.Publisher("/simu_fastsim/odom", Odometry, queue_size = 10)		
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


	def send_W(self):
		self.send_data_W = Float32MultiArray()
		print(len(self.W))
		for xPos in range(11):
			for yPos in range(11):
				max = 0.0
				id = -1
				for action in range(8):
					if not(str(xPos)+'-'+str(yPos)+'-'+str(action) in self.W.keys()):
						self.W[str(xPos)+'-'+str(yPos)+'-'+str(action)] = 0.0
					if max < self.W[str(xPos)+'-'+str(yPos)+'-'+str(action)]:
						max = self.W[str(xPos)+'-'+str(yPos)+'-'+str(action)]
						id = k
				self.send_data_W.data.insert(yPos+xPos*11,id)
		self.pub.publish(self.send_data_W)
		print(len(self.W))



	def selection_action(self):
		tab_proba_action = np.zeros((8,1))
		somme_exp = 0
		for i in range(8):
			somme_exp = somme_exp + np.exp(self.W[self.state+'-'+str(i)]/self.tau)
		for i in range(8):
			tab_proba_action[i] = np.exp(self.W[self.state+'-'+str(i)]/self.tau) / somme_exp
		self.action = self.discreteProb(tab_proba_action)


	def callback_vitesse_sim(self, data):
		self.bool_slow = data.data

	def callback_affichage_W(self,data):
		self.affichage = data.data

	def stopSimulaion(self):
		self.stopSim = True
		
	def rl_loop(self):
		print ("loop")
		#Odom permet de recuperer la position courante du robot
		#rospy.Subscriber("/odom_normalisee", Odometry, self.callback_odom)
		rospy.Subscriber("/slow", Bool, self.callback_vitesse_sim)
		rospy.Subscriber("/affichage_W", Bool, self.callback_affichage_W)

		#Wait for service permet d'attendre que le service de deplacement du robot soit utilisable
		rospy.wait_for_service('deplacement_normalisee')
		rospy.wait_for_service('teleport_normalisee')
		rospy.wait_for_service('fake_deplacement_normalisee')
		#Boucle principale		
		while (not rospy.is_shutdown() | ( self.stopSim)):	
			try:
				self.reward = 0.0
				if self.state == '':
					self.state = str(self.x) +'-'+str(self.y)
				self.last_state = self.state

				#print("W "+str(self.W)+"\n")
				for i in range(8):
					if not (self.state+'-'+str(i) in self.W.keys()) :
						self.W[self.state+'-'+str(i)] = 0.0

				if not ( self.V.has_key(self.state)):
					#print('Nouvelle case')
					self.V[self.state] = 0.0
					#print(self.V[self.state])
				self.selection_action() #selection de l'action

				deplacement = rospy.ServiceProxy('deplacement_normalisee', fake_deplacement_normalisee)
				tab = Float32MultiArray()
				tab.data = [self.action]           #Placer Ici la case vers laquelle se deplacer comme detaillee dans le readme
				resp1 = deplacement(tab)
				self.reward = resp1.rew.data
				self.state = str(int(resp1.new_pos.data[0])) + '-' + str(int(resp1.new_pos.data[1]))  #on recupere les nouvelles positions x et y

				for i in range(8):
					if not (self.state+'-'+str(i) in self.W.keys()):
						self.W[self.state+'-'+str(i)] = 0.0
				if not (self.state in self.V.keys()):
					self.V[self.state] = 0.0


				delta = self.reward + self.gamma * self.V[self.state] - self.V[self.last_state]  #prediction error
				self.W[self.last_state+'-'+str(self.action)] = self.W[self.last_state+'-'+str(self.action)] + self.alphaA * delta
				self.V[self.last_state] = self.V[self.last_state] + self.alphaC * delta
				if(self.W[self.last_state+'-'+str(self.action)] != 0):
					print('changed')
					print(self.last_state)
					print(self.action)
					#self.bool_slow = True

				if(self.reward == 100.0):
					print('reward')
					teleport = rospy.ServiceProxy('teleport_normalisee', deplacement_normalisee)
					tab = Float32MultiArray()
					tab.data.insert(1,9)
					tab.data.insert(2,1)
					odom.pose.pose.position.x = 32 + 9 * 63
					odom.pose.pose.position.y = 32 + 1 * 63
					self.pub_odom.publish(odom)
					tp = teleport(tab)
					#self.state = str(tab.data[0]) + ' ' + str(tab.data[1])
				if(self.bool_slow):
					time.sleep(1.0)
				time.sleep(0.075)
				if(self.affichage):
					self.send_W()
					self.affichage = False
			except rospy.ServiceException, e:
				print "Service call failed: %s"%e

		# end while
		print("---end while ")
#-------------------------------------------
if __name__ == '__main__':
	h = Rl()
	rospy.init_node('deplacement_case', anonymous=True)
	try:
		h.rl_loop()
	except rospy.ROSInterruptException: pass

def createRL(dico):
	instance = Rl()
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
	
	print("----TP-----")
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