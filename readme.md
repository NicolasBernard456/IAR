Tuto d'installation :
	 
	 0) Nous considérons que Ros est correctement intallé sur vos machines
	 1) cd ~/catkin_ws/src
	 2) git clone https://github.com/NicolasBernard456/IAR_HRL.git
 	 3) cd ~/catkin_ws/src/IAR/libfastsim
	 4) ./waf configure
	 5) ./waf build
	 6) cd ~/catkin_ws/
	 7) catkin_make --pkg fastsim      ( 2 fois si besoin ) 
	 8) catkin_make --pkg hrl          ( 2 fois si besoin ) 
	 9) Pour verifier l'installation la commande -> 'catkin_make' doit compiler à 100 % sans ereurs

Pour lancer la simulation : 

	-1) Dans un terminal  => roslaunch hrl labyrinthe.launch
	-2) Dans un terminal  => rosrun hrl main_hrl.py 
Pour déplacer le robot de case en case:

	-Dans un terminal : rosservice call /deplacement_normalisee *faire tab*
	Le terminal devrait afficher :
	
	rosservice call /deplacement_normalisee "pos:
 	 layout:
   	 dim:
    	- label: ''
    	  size: 0
    	  stride: 0
    	data_offset: 0
  	data:
 	 - 4"
  
  
  Modifier la derniere valeur correspondant a la case vers laquelle se déplacer:
  
  Schéma :
  
 	* correspond au robot et les chiffres, les cases vers lesquelles le robot peut se déplacer
 	7 8 9
	4 * 6
  	1 2 3
  
