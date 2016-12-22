#include "ros/ros.h"
#include "std_msgs/Float32MultiArray.h"

#include <sstream>

/**
 * This tutorial demonstrates simple sending of messages over the ROS system.
 */
int main(int argc, char **argv){
	ros::init(argc, argv, "talker");

	ros::NodeHandle n;

	ros::Publisher chatter_pub = n.advertise<std_msgs::Float32MultiArray>("/next_pose", 1000);
	if (argc == 3){
		ros::Rate poll_rate(100);
		while(chatter_pub.getNumSubscribers() == 0)
			poll_rate.sleep();
		std_msgs::Float32MultiArray msg;
		msg.data.push_back(atof(argv[1]));
		msg.data.push_back(atof(argv[2]));
		chatter_pub.publish(msg);
		ros::spinOnce();
	}
	else 
		ROS_ERROR("Besoin de 2 arguments (x et y) position du robot");

	return 0;
}