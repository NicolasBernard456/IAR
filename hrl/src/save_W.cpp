#include <ros/ros.h>
#include <std_msgs/Float32MultiArray.h>

bool test = true;

void cb(std_msgs::Float32MultiArray msg){
	test = false;
	FILE *f = fopen("save_W.txt","w");
	for(int i = 0 ; i < msg.data.size() ; i++){
		std::string s = boost::lexical_cast<std::string>(msg.data[i]);
		fputs(s.c_str(),f);
		fputc(' ',f);
		if(i % 3 == 0)
			fputc('\n',f);
	}
	fclose(f);
	std::cout << "OKOKOK" << std::endl;	
}


int main(int argc, char **argv){
	ros::init(argc,argv,"save_W");
	ros::NodeHandle n;
	ros::Subscriber sub = n.subscribe("/Wsended",1 , cb);
	while(ros::ok())
		ros::spinOnce();
	return 0;
}