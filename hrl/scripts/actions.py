#!/usr/bin/env python
class Actions:
    def action_N(posX,posY):
         newPosX = posX-1
         newPosY = posY
         return [newPosX,newPosY]
        
    def action_NE(posX,posY):
         newPosX = posX-1
         newPosY = posY+1
         return [newPosX,newPosY]
        
    def action_E(posX,posY):
         newPosX = posX
         newPosY = posY+1
         return [newPosX,newPosY]
        
    def action_SE(posX,posY):
         newPosX = posX+1
         newPosY = posY+1
         return [newPosX,newPosY]

    def action_S(posX,posY):
         newPosX = posX+1
         newPosY = posY
         return [newPosX,newPosY]
        
    def action_SW(posX,posY):
         newPosX = posX+1
         newPosY = posY-1
         return [newPosX,newPosY]
        
    def action_W(posX,posY):
         newPosX = posX
         newPosY = posY-1
         return [newPosX,newPosY]
        
    def action_NW(posX,posY):
         newPosX = posX-1
         newPosY = posY-1
         return [newPosX,newPosY]

    def action_NaN(posX,posY):
         newPosX = posX
         newPosY = posY
         return [newPosX,newPosY]
        
#-------------------------------------------
########## ACTION ENUM ###################
class Enum_Action:
    
    NORTH = Actions.action_N 
    NORTH_EAST = Actions.action_NE
    EAST= Actions.action_E
    SOUTH_EAST =  Actions.action_SE
    SOUTH =  Actions.action_S
    SOUTH_WEST =  Actions.action_SW
    WEST =  Actions.action_W
    NORTH_WEST =  Actions.action_NW
    NaN =  Actions.action_NaN
#-------------------------------------------