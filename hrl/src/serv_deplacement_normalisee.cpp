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
#include <opencv2/core/core.hpp>
#include <opencv2/opencv.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
ros::ServiceClient cl;
int x_odom, y_odom;

bool deplacement_case(int* x, int* y, int dep){
	int old_x = *x , old_y = *y;
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
	tp_req.x = 32 + norm_x * 63;	//Converison en cood pixels
	tp_req.y = 32 + norm_y * 63;	//Converison en cood pixels
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
// 		resp.rew.data = -0.1;
	return true;
}
void cb_odom(nav_msgs::Odometry odom){	//REcupere la position courrante du robot
	x_odom = odom.pose.pose.position.x;	
	y_odom = odom.pose.pose.position.y;
}
static void arrowedLine(cv::Mat img, cv::Point pt1, cv::Point pt2, const cv::Scalar& color,int thickness=1, int line_type=8, int shift=0, double tipLength=0.1)
{
    const double tipSize = norm(pt1-pt2)*tipLength; // Factor to normalize the size of the tip depending on the length of the arrow
    cv::line(img, pt1, pt2, color, thickness, line_type, shift);
    const double angle = atan2( (double) pt1.y - pt2.y, (double) pt1.x - pt2.x );
    cv::Point p(cvRound(pt2.x + tipSize * cos(angle + CV_PI / 4)),
    cvRound(pt2.y + tipSize * sin(angle + CV_PI / 4)));
    cv::line(img, p, pt2, color, thickness, line_type, shift);
    p.x = cvRound(pt2.x + tipSize * cos(angle - CV_PI / 4));
    p.y = cvRound(pt2.y + tipSize * sin(angle - CV_PI / 4));
    cv::line(img, p, pt2, color, thickness, line_type, shift);
}


std::vector<int> arrow_points(float W, int x, int y){
	std::vector<int> tab;
	if(W == 0){
		tab.push_back(x);
		tab.push_back(y + 25);
		tab.push_back(x);
		tab.push_back(y - 25);
	}
	else if(W == 1){
		tab.push_back(x - 25);
		tab.push_back(y + 25);
		tab.push_back(x + 25);
		tab.push_back(y - 25);
	}
	else if(W == 2){
		tab.push_back(x - 25);
		tab.push_back(y);
		tab.push_back(x + 25);
		tab.push_back(y);
	}
	else if(W == 3){
		tab.push_back(x - 25);
		tab.push_back(y - 25);
		tab.push_back(x + 25);
		tab.push_back(y + 25);
	}
	else if(W == 4){
		tab.push_back(x);
		tab.push_back(y - 25);
		tab.push_back(x);
		tab.push_back(y + 25);
	}
	else if(W == 5){
		tab.push_back(x + 25);
		tab.push_back(y - 25);
		tab.push_back(x - 25);
		tab.push_back(y + 25);
	}	
	else if(W == 6){
		tab.push_back(x + 25);
		tab.push_back(y);
		tab.push_back(x - 25);
		tab.push_back(y);
	}
	else if(W == 7){
		tab.push_back(x + 25);
		tab.push_back(y + 25);
		tab.push_back(x - 25);
		tab.push_back(y - 25);
	}
	else{
		tab.push_back(x);
		tab.push_back(y);
		tab.push_back(x);
		tab.push_back(y);
	}
		
	return tab;
}

void W_sended(std_msgs::Float32MultiArray W){
	char* pPath;
  	pPath = getenv ("ROS_PACKAGE_PATH");
	std::string myString = std::string(pPath); 
	std::string token;
	cv::Mat img;
	while((token != myString) && (!img.data)){
		printf("%d\n", !img.data); 
  		token = myString.substr(0,myString.find_first_of(":"));
  		myString = myString.substr(myString.find_first_of(":") + 1);
		std::string res = (token.c_str());
		res = res+"/IAR/hrl/envs/labyrinthe.pbm";
		img = cv::imread(res, CV_LOAD_IMAGE_COLOR);
	}

	//cv::Mat img = cv::imread("/home/viki/catkin_ws/src/IAR/hrl/envs/labyrinthe.pbm", CV_LOAD_IMAGE_COLOR);
	std::cout << W.data.size() << std::endl;
	for(int i = 0 ; i < 11 ; i++){
		for(int j = 0 ; j < 11 ; j ++){
			
			int i_x = 32 + i * 63;
			int j_y = 32 + j * 63;
			float value_W =  static_cast<int>(W.data[j+11*i]);
			if(value_W != -1){
				std::cout << value_W << std::endl;
				std::cout << i << " " << j << std::endl;
			}
			std::vector<int> tab = arrow_points(value_W,i_x,j_y);
			arrowedLine(img,cv::Point(tab[0],tab[1]),cv::Point(tab[2],tab[3]),cv::Scalar(0,0,0));
		}
	}
// 	arrowedLine(img,cv::Point(0,0),cv::Point(500,100),cv::Scalar(0,0,0));
	
	cv::namedWindow( "Display", cv::WINDOW_NORMAL );// Create a window for display.
	
	if (!img.empty()) {
		cv::imshow( "Display", img );                   // Show our image inside it.
	}
	cv::waitKey(0);                                          // Wait for a keystroke in the window
	
	
	
	
}

int main(int argc, char* argv[]){

	ros::init(argc,argv,"serv_deplacement_normalisee");
	ros::NodeHandle n;
	
	ros::ServiceServer serv_telep = n.advertiseService("/teleport_normalisee" , teleport_serveur);
	ros::ServiceServer serv_deplacement = n.advertiseService("/deplacement_normalisee" , deplacement_serveur);
	ros::ServiceServer serv_fake_deplacement = n.advertiseService("/fake_deplacement_normalisee" , fake_deplacement_serveur);
	ros::Subscriber sub_odom_norm = n.subscribe("/odom_normalisee", 1 , cb_odom);
	ros::Subscriber sub_sendedW = n.subscribe("/Wsended",1 , W_sended);
	cl = n.serviceClient<fastsim::Teleport>("/simu_fastsim/teleport");
	ros::spin();


 	

	return 0;
}
