#!/usr/bin/env python
import numpy as np;
from maps import *
from actions import *



    
class Simulation():
    #-----------------------Constructeur--------------------
    def __init__(self,typeMap,posX,posY):
        """
            typeMap : parametre de type Enum_Maps 
        """
        self.usedMap = Maps.selectMap(typeMap)
        self.startPositionX = posX
        self.startPositionY = posY
        self.currentPosX = startPositionX
        self.currentPosY = startPositionY
        self.oldAction = Enum_Action.NaN
        self.nextAction = Enum_Action.NaN

    def getNextPosition(self):
        """
            Retourne la future case en fct de l'action à faire.
        """
        [newPosX,newPosY,canMove] = Maps.getNextPosition(self.usedMap, self.currentPosX,self.currentPosY,self.nextAction)
        return [newPosX,newPosY]

    def canExecuteNextAction(self):
        """
            Test si l'action "nextAction" est possible .
        """
        [newPosX,newPosY,canMove] = Maps.getNexPosition(self.usedMap,self.currentPosX,self.currentPosY,self.nextAction)
        return canMove
    
    def executeAction(self):
        if self.canExecuteNextAction:
            [newPosX,newPosY] = self.getNextPosition()
            self.oldAction =  self.nextAction
            self.nextAction = Enum_Action.NaN
            self.currentPosX = newPosX
            self.currentPosY = newPosY
            print("currentPosX "+str(self.currentPosX))
            print("currentPosY "+str(self.currentPosY))
            print("\n")
            
    def setAction(self,nextAction):
        self.nextAction = nextAction
#-------------------------------------------
if __name__ == '__main__':
    #-------Exemple d'utilisation------
    startPositionX = 2
    startPositionY = 2
    
    print("startPositionX "+str(startPositionX))
    print("startPositionY "+str(startPositionY))
    print("\n")
    Sim = Simulation(Enum_Maps.MAP_ALL,startPositionX,startPositionY)
    
    Sim.setAction(Enum_Action.EAST)
    Sim.executeAction()

    Sim.setAction(Enum_Action.SOUTH)
    Sim.executeAction()
    
    print ("end main Simulation")