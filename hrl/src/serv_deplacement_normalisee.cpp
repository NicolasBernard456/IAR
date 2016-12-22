#include <ros/ros.h>
#include <std_msgs/Float32MultiArray.h>
#include <hrl/deplacement_normalisee.h>
#include <hrl/deplacement_normaliseeRequest.h>
#include <hrl/deplacement_normaliseeResponse.h>
#include <fastsim/Teleport.h>
#include <fastsim/TeleportRequest.h>
#include <fastsim/TeleportResponse.h>


ros::ServiceClient cl;

bool deplacement_serveur(hrl::deplacement_normaliseeRequest& req, hrl::deplacement_normaliseeResponse& resp){
	cl.waitForExistence();
	if(req.pos.data.size() != 2){
		ROS_ERROR("Erreur sur la request serveur");
		return false;
	}
	int norm_x = req.pos.data[0], norm_y = req.pos.data[1];
	if(norm_x < 0 || norm_x > 11 || norm_y < 0 || norm_y > 11){
		ROS_ERROR("Erreur sur la request serveur");
		return false;
	}
	fastsim::TeleportRequest tp_req;
	fastsim::TeleportResponse tp_resp;
	tp_req.x = 32 + norm_x * 60 + 3 * norm_x;
	tp_req.y = 32 + norm_y * 60 + 3 * norm_y;
	tp_req.theta = 0;
	cl.call(tp_req,tp_resp);
	return tp_resp.ack;
}


int main(int argc, char* argv[]){
	ros::init(argc,argv,"serv_deplacement_normalisee");
	ros::NodeHandle n;
	
	ros::ServiceServer serv = n.advertiseService("/deplacement_normalisee" , deplacement_serveur);
	cl = n.serviceClient<fastsim::Teleport>("/simu_fastsim/teleport");
	
	ros::spin();
	return 0;
	
	
}