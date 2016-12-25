Pour lancer la simu : roslaunch hrl labyrinthe.launch
Pour déplacer le robot de case en case:
	-Sur un terminal : rosservice call /deplacement_normalisee *faire tab*
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
  