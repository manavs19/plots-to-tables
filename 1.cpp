#include <iostream>
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>

using namespace std;
using namespace cv;


int main()
{
	Mat img;
	img = imread("data/1.png", CV_LOAD_IMAGE_COLOR);
	namedWindow("my window", CV_WINDOW_NORMAL);
	imshow("my window", img);
	waitKey(0);
	return 0;
}