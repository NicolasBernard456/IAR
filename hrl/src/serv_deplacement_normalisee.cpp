#include <ros/ros.h>
#include <std_msgs/Float32MultiArray.h>
#include <hrl/deplacement_normalisee.h>
#include <hrl/deplacement_normaliseeRequest.h>
#include <hrl/deplacement_normaliseeResponse.h>
#include <hrl/fake_deplacement_normalisee.h>
#include <hrl/fake_deplacement_normaliseeRequest.h>
#include <hrl/fake_deplacement_normaliseeResponse.h>
#include <fastsim/Teleport.h>
#include <fastsim/TeleportRequest.h>
#include <fastsim/TeleportResponse.h>
#include <nav_msgs/Odometry.h>


ros::ServiceClient cl;
int x_odom, y_odom;


bool deplacement_case(int* x, int* y, int dep){
	int old_x = *x , old_y = *y;
// 	std::cout << "x = " << *x << " y = " << *y << std::endl;

// 	if(dep < 1 || dep > 10 || dep == 5)
// 		return false;
// 	
// 	if (dep == 8)
// 		*y = *y - 1; 
// 	else if (dep == 9){
// 		*x = *x + 1;
// 		*y = *y - 1; 
// 	}
// 	else if (dep == 6)
// 		*x = *x + 1;
// 	else if (dep == 3){
// 		*x = *x + 1;
// 		*y = *y + 1;		
// 	}
// 	else if (dep == 2)
// 		*y = *y + 1;
// 	else if (dep == 1){
// 		*y = *y + 1;
// 		*x = *x - 1;
// 	}
// 	else if (dep == 4)
// 		*x = *x - 1;
// 	else if(dep == 7){
// 		*y = *y - 1;
// 		*x = *x - 1;
// 	}
	if(dep < 0 || dep > 8)
		return false;
	
	if (dep == 0)
		*y = *y - 1; 
	else if (dep == 1){
		*x = *x + 1;
		*y = *y - 1; 
	}
	else if (dep == 2)
		*x = *x + 1;
	else if (dep == 3){
		*x = *x + 1;
		*y = *y + 1;		
	}
	else if (dep == 4)
		*y = *y + 1;
	else if (dep == 5){
		*y = *y + 1;
		*x = *x - 1;
	}
	else if (dep == 6)
		*x = *x - 1;
	else if(dep == 7){
		*y = *y - 1;
		*x = *x - 1;
	}
	
	
	
	
	//On verifie qu'on ne se cogne pas sur un mur
	if((*x < 0 || *x > 10 || *y < 0 || *y > 10) || (*x == 5 && !(*y == 9 || *y == 2)) || (*y == 5 && (*x < 5 && *x != 1)) || (*y == 6 && (*x > 5 && *x != 8)) ){ //Le labyrinthe est de taille 11 * 11
		*x = old_x;
		*y = old_y;
		return false;
	}
	return true;
// 	std::cout << "x = " << *x << " y = " << *y << std::endl;
}


bool teleport_serveur(hrl::deplacement_normaliseeRequest& req, hrl::deplacement_normaliseeResponse& resp){
	cl.waitForExistence();
	if(req.pos.data.size() != 2){	//On doit avoir les coord x et y du robot pour le teleporter
		ROS_ERROR("Erreur sur la request serveur");
		return false;
	}
	int norm_x = req.pos.data[0], norm_y = req.pos.data[1];	//Valeur x et y normalisees (Chaque rangee de case est une valeur de y et chaque colonne est une valeur de x)
	if(norm_x < 0 || norm_x > 10 || norm_y < 0 || norm_y > 10){ //Le labyrinthe est de taille 11 * 11
		ROS_ERROR("Erreur sur la request serveur");
		return false;
	}
	fastsim::TeleportRequest tp_req;	//REquest pour le serveur TP (utilisant des pixels)
	fastsim::TeleportResponse tp_resp;
	tp_req.x = 32 + norm_x * 60 + 3 * norm_x;	//Converison en cood pixels
	tp_req.y = 32 + norm_y * 60 + 3 * norm_y;	//Converison en cood pixels
	tp_req.theta = 0;
	cl.call(tp_req,tp_resp);
}

bool deplacement_serveur(hrl::fake_deplacement_normaliseeRequest& req, hrl::fake_deplacement_normaliseeResponse& resp){
	cl.waitForExistence();
	if(req.pos.data.size() != 1){	//On doit avoir une des 8 cases autour du robot(1 à 8,haut , haut+droite, etc , haut + gauche)
		ROS_ERROR("Erreur sur la request serveur");
		return false;
	}
	int pos = req.pos.data[0];	//Case selctionne
	int norm_x = x_odom, norm_y = y_odom;	//Valeur x et y normalisees (Chaque rangee de case est une valeur de y et chaque colonne est une valeur de x)
	bool mur = deplacement_case(&norm_x, &norm_y, pos);
	fastsim::TeleportRequest tp_req;	//REquest pour le serveur TP (utilisant des pixels)
	fastsim::TeleportResponse tp_resp;
	tp_req.x = 32 + norm_x * 60 + 3 * norm_x;	//Converison en cood pixels
	tp_req.y = 32 + norm_y * 60 + 3 * norm_y;	//Converison en cood pixels
	tp_req.theta = 0;
	cl.call(tp_req,tp_resp);
	resp.rew.data = 0;
	if(norm_x == 2 && norm_y == 7)
		resp.rew.data = 100;
	resp.new_pos.data.push_back(norm_x);
	resp.new_pos.data.push_back(norm_y);
// 	else if(!mur)
// 		resp.rew.data = -1;
	return true;
}

bool fake_deplacement_serveur(hrl::fake_deplacement_normaliseeRequest& req, hrl::fake_deplacement_normaliseeResponse& resp){
	cl.waitForExistence();
	if(req.pos.data.size() != 1){	//On doit avoir une des 8 cases autour du robot(1 à 8,haut , haut+droite, etc , haut + gauche)
		ROS_ERROR("Erreur sur la request serveur");
		return false;
	}
	int pos = req.pos.data[0];	//Case selctionne
	int norm_x = x_odom, norm_y = y_odom;	//Valeur x et y normalisees (Chaque rangee de case est une valeur de y et chaque colonne est une valeur de x)
	bool mur = deplacement_case(&norm_x, &norm_y, pos);
	resp.rew.data = 0;
	resp.new_pos.data.push_back(norm_x);
	resp.new_pos.data.push_back(norm_y);
	if(norm_x == 2 && norm_y == 7)
		resp.rew.data = 100;
// 	else if(!mur)
// 		resp.rew.data = -1;
	return true;
}
void cb_odom(nav_msgs::Odometry odom){	//REcupere la position courrante du robot
	x_odom = odom.pose.pose.position.x;	
	y_odom = odom.pose.pose.position.y;
}

int main(int argc, char* argv[]){
	ros::init(argc,argv,"serv_deplacement_normalisee");
	ros::NodeHandle n;
	
	ros::ServiceServer serv_telep = n.advertiseService("/teleport_normalisee" , teleport_serveur);
	ros::ServiceServer serv_deplacement = n.advertiseService("/deplacement_normalisee" , deplacement_serveur);
	ros::ServiceServer serv_fake_deplacement = n.advertiseService("/fake_deplacement_normalisee" , fake_deplacement_serveur);
	ros::Subscriber sub_odom_norm = n.subscribe("/odom_normalisee", 1 , cb_odom);
	cl = n.serviceClient<fastsim::Teleport>("/simu_fastsim/teleport");
	ros::spin();
	return 0;
}