#include "ros/ros.h"
#include "hrl/deplacement_normalisee.h"
#include "hrl/deplacement_normaliseeRequest.h"
#include "hrl/deplacement_normaliseeResponse.h"


int main(int argc, char **argv){
	ros::init(argc, argv, "client_deplacement_normalisee");
	ros::NodeHandle n;

	ros::ServiceClient client = n.serviceClient<hrl::deplacement_normalisee>("/teleport_normalisee");
	hrl::deplacement_normaliseeRequest req;
	req.pos.data.push_back(atof(argv[1]));
	req.pos.data.push_back(atof(argv[2]));
	hrl::deplacement_normaliseeResponse resp;
	client.call(req,resp);
// 	ros::spin();

	return 0;
}