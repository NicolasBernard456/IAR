#include <ros/ros.h>
#include <nav_msgs/Odometry.h>



//Noeud publiant sur le topic /odom_normalisee la poistion normalisee du robot sur le labyrinthe.
ros::Publisher pub_odom;



void Callback_odom(nav_msgs::Odometry odom){
	nav_msgs::Odometry odom_normalisee;
	odom_normalisee.header.frame_id = odom.header.frame_id;
	odom_normalisee.pose.pose.position.x = (odom.pose.pose.position.x - 32) / 63;	//Conversion pixel position
	odom_normalisee.pose.pose.position.y = (odom.pose.pose.position.y - 32) / 63;
	pub_odom.publish(odom_normalisee);
}

int main(int argc, char **argv){
	ros::init(argc,argv,"odom_normalisee");
	ros::NodeHandle n;
	
	ros::Subscriber sub_odom = n.subscribe("/simu_fastsim/odom", 1, Callback_odom);
	pub_odom = n.advertise<nav_msgs::Odometry>("/odom_normalisee", 1);
	ros::spin();
	return 0; 
}