#!/usr/bin/env python
import numpy as np;
from actions import *
class Maps:
    """
     La classe Maps est une classe qui genere les maps utilisees pour la simulation
    """
    #Nommage des salles
    #+----+----+
    #| A  | B  |
    #|    |    |
    #+----+----+
    #| D  | C  |
    #|    |    |
    #+----+----+
    def globalMap():
        return np.array([
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
            [1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
            ])
    
    def mapAB():
        return np.array([
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
            [1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1]
            ])
        
    def  mapDC():
        return np.array([
            [1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
            ])
    
    def mapAD():
        return np.array([
            [1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 1, 0, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1,]
            ])
    
    def mapBC():
        return np.array([
            [1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 0, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1]
            ])

    def selectMap(typeMap):
        """
        Cette fonction retourne une map en fonction de l'enum passe en parametre.
        typeMap : parametre de type Enum_Maps 
        """
        return typeMap()

    def isInMap(map,posX,posY):
        """
        Test si (posX,posY) sont dans la carte
        """
        if ((posX >= map.shape[0]) |(posY >= map.shape[1])):
            return False
        return True

    def isWall(map,posX,posY):
        """
            Test si la case en (posX,posY) est un mur
        """
        if not Maps.isInMap(map,posX,posY):
             raise IndexError(" (psX,posY) is not in the map !")
        if map[posX,posY] == 1:
            return True
        return False
    
    def getNextPosition(map,posX,posY,action):
        # Test si le robot est deja dans une case de type mur
        if Maps.isWall(map,posX,posY):
            raise ValueError("The robot is in a wall !")
        [newPosX,newPosY] = action(posX,posY)
        
        # Test si la nouvelle postion est sur la map ou si c'est un mur
        if ((not Maps.isInMap(map,newPosX,newPosY)) | (Maps.isWall(map,newPosX,newPosY))):
            return [posX,posY,False] # on ne bouge pas
        else:
            return [newPosX,newPosY,True] 

            
#-------------------------------------------
########## MAP ENUM ###################
class Enum_Maps:
    """
    Enum compose de pointeur de fonction vers les fonctions de la classe Maps
    """
    
    MAP_ALL = Maps.globalMap
    MAP_AB = Maps.mapAB
    MAP_DC = Maps.mapDC
    MAP_AD = Maps.mapAD
    MAP_BC = Maps.mapBC
    
    #Nommage des salles
    #+----+----+
    #| A  | B  |
    #|    |    |
    #+----+----+
    #| D  | C  |
    #|    |    |
    #+----+----+
    
if __name__ == '__main__':
    #-------Exemple d'utilisation------ 
    #print (Maps.globalMap())
    #print (Maps.mapBC())
    #print (Maps.selectMap(Enum_Maps.MAP_BC))
    
    #usedMaps  = Maps.selectMap(Enum_Maps.MAP_ALL)
    #print (usedMaps)
    
    posX = 2
    posY = 2
    print("OldPosX "+str(posX))
    print("OldPosY "+str(posY))
    usedMaps  = Maps.selectMap(Enum_Maps.MAP_ALL)
    [newPosX,newPosY,canMove] = Maps.getNextPosition(usedMaps,posX,posY,Enum_Action.WEST)
    print("newPosX "+str(newPosX))
    print("newPosY "+str(newPosY))
    
    print ("end main maps")
