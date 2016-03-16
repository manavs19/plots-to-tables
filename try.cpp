#include <iostream>
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <vector>
#include <math.h>
#include  <opencv2/imgproc/imgproc.hpp>
#include <fstream>

using namespace std;
using namespace cv;

#define PERCENT_THRESH 0.15
#define DEBUG 0


////////////////////Documentation////////////////////////////////////
/////////////////////Aranya Dan//////////////////////////////////////
//**1)extract_points(Mat img, int hue,int ten_length)-->/////////////
//    This function calculates the points inside the image //////////
//    of a particular curve provided as input.             //////////
// Parameters-                                             //////////
//    Mat-->image of an isolated curve                     //////////
//    int hue--> hue value of that curve                   //////////
//    int ten_length--> pixel distance between which 10    //////////
//                      points are calculated. Sending 0   //////////
//                      calculates 10 points in the whole  //////////
//                      image.                             //////////
// Return value--> a vector of cv::Points.                 //////////
//                                                         //////////
//**2)vector<vector<Point> >  findplot(Mat img)-->         //////////
//    This function calculates hue values and segments     //////////
//    curves based on that.                                //////////
// Parameters-                                             //////////
//    Mat-->image of the cropped graph                     //////////
// Return value--> a vector of vector of points            //////////
//              Hue values are stored in the variable      //////////
//              curveclrHSV. Index of that can be used     //////////
//              to find the index of the graph.            //////////
//**3)vector<vector<Point> >  findplot(Mat,vector<int>) -->//////////
//    Overloaded function with additional input of int     //////////
//    vector containing hue values.                        //////////
//                                                         //////////
//    MACROS- DEBUG(for debugging)                         //////////
//            DEBUG=1 shows points on the curve            //////////
//            PERCENT_THRESH(for fine tuning plot size)    //////////
//                           (used in findplot(Mat))       //////////
//////////////////aranya.dan1996@gmail.com///////////////////////////
/////////////////////////////////////////////////////////////////////
//   The output, vector of vector of Point, is given in   ///////////
//   opencv coordinate system. For normal cartesian system, /////////
//   the y value will be (img.rows - y).                    /////////
/////////////////////////////////////////////////////////////////////


//Function to exract points from a graph
vector<Point> extract_points(Mat img, int hue,int ten_length)
{
  if(ten_length == 0)
    ten_length = img.cols;

  vector<Point> extracted_points;
  int iterated_c=0;
  int yavg = 0;
  int yavgcnt=0;
  int minx=img.cols-1,maxx=0;


  //Counting start and end of the graphs
  for(int c=0;c<img.cols;c++)
  {
    for(int r=0;r<img.rows;r++)
    {
      if(img.at<Vec3b>(r,c)[0]> hue - 5 && img.at<Vec3b>(r,c)[0]< hue + 5)
      {
        minx=c;
        c=img.cols;
        break;
      }
    }
  }
  for(int c=img.cols-1;c>=0;c--)
  {
    for(int r=0; r<img.rows; r++)
    {
      if(img.at<Vec3b>(r,c)[0]> hue - 5 && img.at<Vec3b>(r,c)[0]< hue + 5)
      {
        maxx=c;
        c=-1;
        break;
      }
    }
  }



  //cout<<"min-"<<minx<<"max-"<<maxx<<endl;
  vector<Point> iterations;
  for(int c=0;c<img.cols;c++)
  {
    int ycol=0;
    int count=0;

    //checking heads
    vector<int> heads;
    int lastpixrow;
    for(int r=0;r<img.rows;r++)
    { //computes avg y for each column
      if(img.at<Vec3b>(r,c)[0]> hue - 5 && img.at<Vec3b>(r,c)[0]< hue + 5)
      {
        if(heads.size()==0)
        {
          heads.push_back(r);
          lastpixrow=r;
        }

        if((r-lastpixrow)>5)
        {
          heads.push_back(r);
          lastpixrow=r;
        }
        else
        {
          lastpixrow=r;
        }
      }
    }
    int starter=0;
    if(heads.size()>1)
    {
      if(iterations.size()==0)
      {
        starter =0;
      }
      else
      {
        int mindist=99999999;
        for(int m=0; m<heads.size();m++)
        {
          //circle(img,Point(heads[m],c),4,Scalar(90,180,180),1);
          Point lastpoint=iterations[iterations.size()-1];
          if((abs(heads[m]-lastpoint.y) + abs(c-lastpoint.x))<mindist)
          {
            mindist=(abs(heads[m]-lastpoint.y) + abs(c-lastpoint.x));
            starter=heads[m];
          }
        }
      }
    }
    //checking heads

    lastpixrow=-1;
    for(int r=starter;r<img.rows;r++)
    {
      //computes avg y for each column
      if(img.at<Vec3b>(r,c)[0]> hue - 5 && img.at<Vec3b>(r,c)[0]< hue + 5)
      {
        if(lastpixrow!=-1)
        {
          if((r-lastpixrow)>5)
            break;
        }
        count ++;
        ycol += r;
        lastpixrow = r;
      }
    }
    if(count !=0)
    {
      yavgcnt++;
      yavg+=int((ycol)/count);
      iterations.push_back(Point(int(ycol/count),c));
    }
    ycol=count=0;
    if(c > 0 && c % int(ten_length/10) == 0)
    { //computes the averaged out point in the line between min lengths
      Point ex;
      ex.x=int(iterated_c + int(ten_length / 20));
      if(yavgcnt!=0)
        ex.y = (img.rows - int(yavg / yavgcnt));
      if(yavgcnt == 0 && extracted_points.size() > 2)
      {
        int deltax=(extracted_points[extracted_points.size()-1].x - extracted_points[extracted_points.size()-2].x);
        int deltay=(extracted_points[extracted_points.size()-1].y - extracted_points[extracted_points.size()-2].y);
        double m=double(deltay)/double(deltax);
        ex.y=int(extracted_points[extracted_points.size()-1].y + m * double(deltax));
      }
      iterated_c = c;
      if(ex.x < minx || ex.x > maxx)
      {
        //cout<<"1"<<endl;
        /////////Add handle for outside points///////
        extracted_points.push_back(Point(ex.x,-1));
        continue;
      }
      extracted_points.push_back(ex);
      //cout<<"x="<<ex.x<<"y="<<ex.y<<endl;
      yavg=yavgcnt=0;
    }
  }
  if(DEBUG == 1)
  {
    cvtColor(img, img, CV_HSV2BGR);
    for(int i=0;i<extracted_points.size();i++)
    {
      circle(img, Point(extracted_points[i].x,img.rows - extracted_points[i].y),1,Scalar(255,255,255),1);
    }
    imshow("curves",img);
    waitKey(0);
  }

  return extracted_points;
}
vector<vector<Point> >  findplot(Mat img,int ten_length)
{
	//Image Colour based Segmentation (grayscale removal) to remove axes,text
  for(int i=0; i<img.rows;i++)
  {
    for(int j=0; j<img.cols;j++)
    {

        int a[]={img.at<Vec3b>(i,j)[0],img.at<Vec3b>(i,j)[1],img.at<Vec3b>(i,j)[2]};
        if((*max_element(a,a+2) - *min_element(a,a+2))<2)
        {
          img.at<Vec3b>(i,j)[0] = 0;
          img.at<Vec3b>(i,j)[1] = 0;
          img.at<Vec3b>(i,j)[2] = 0;
        }
    }
  }

  //Converting to HSV and taking a count of the colurs (H) values present
  Mat img2;
  cvtColor(img, img2, CV_BGR2HSV);
  int clor[360];
  for(int i=0;i<360;i++)
    clor[i]=0;

  for(int i=0;i<img2.rows;i++)
  {
    for(int j=0;j<img2.cols;j++)
    {
      clor[(int)img2.at<Vec3b>(i,j)[0]]++;
    }
  }
  //Thresholding to find curves of particuar hue value, storing the color values in a vector
  //Also removing close Hue values
  vector<int> curveclrHSV;
  for(int i=1;i<360;i++)
  {
    if(clor[i] > (img.rows * img.cols) * (PERCENT_THRESH / 100))
    {
      if(curveclrHSV.size()>0)
      {
        if(abs(curveclrHSV[curveclrHSV.size()-1] - i) <3)
        {
          continue;
        }

      }
      if(DEBUG ==4)
        cout<<i<<"-->"<<clor[i]<<endl;
      curveclrHSV.push_back(i);
    }
  }

  vector<vector<Point> > curve_points;
  //Plotting each curve seperately
  Mat nwimg(img.rows,img.cols, CV_8UC3,Scalar(0,0,0));
  for (vector<int>::iterator it = curveclrHSV.begin(); it != curveclrHSV.end(); ++it)
  {
    Mat nwimg(img.rows,img.cols, CV_8UC3,Scalar(0,0,0));
    for(int i=0;i<nwimg.rows;i++)
    {
      for(int j=0;j<nwimg.cols;j++)
      {
        if(img2.at<Vec3b>(i,j)[0]> *it - 5 && img2.at<Vec3b>(i,j)[0]< *it + 5)
        {
          nwimg.at<Vec3b>(i,j)=img2.at<Vec3b>(i,j);
        }
      }
    }
    curve_points.push_back(extract_points(nwimg,*it,ten_length));
    if(DEBUG == 2)
    {
      cvtColor(nwimg, nwimg, CV_HSV2BGR);
      imshow("curves",nwimg);waitKey(0);
    }
  }
  if(DEBUG == 3)
  {
    cvtColor(nwimg, nwimg, CV_HSV2BGR);
    imshow("curves",nwimg);
	  waitKey(0);
  }

	return curve_points;
}
vector<vector<Point> >   findplot(Mat img, vector<int> curveclrHSV,int ten_length)
{
	//Image Colour based Segmentation (grayscale removal) to remove axes,text
  for(int i=0; i<img.rows;i++)
  {
    for(int j=0; j<img.cols;j++)
    {

        int a[]={img.at<Vec3b>(i,j)[0],img.at<Vec3b>(i,j)[1],img.at<Vec3b>(i,j)[2]};
        if((*max_element(a,a+2) - *min_element(a,a+2))<2)
        {
          img.at<Vec3b>(i,j)[0] = 0;
          img.at<Vec3b>(i,j)[1] = 0;
          img.at<Vec3b>(i,j)[2] = 0;
        }
    }
  }

  cvtColor(img, img, CV_BGR2HSV);
  vector<vector<Point> > curve_points;
  //Plotting each curve seperately
  Mat nwimg(img.rows,img.cols, CV_8UC3,Scalar(0,0,0));
  for (vector<int>::iterator it = curveclrHSV.begin(); it != curveclrHSV.end(); ++it)
  {
    Mat nwimg(img.rows,img.cols, CV_8UC3,Scalar(0,0,0));
    for(int i=0;i<nwimg.rows;i++)
    {
      for(int j=0;j<nwimg.cols;j++)
      {
        if(img.at<Vec3b>(i,j)[0]> *it - 5 && img.at<Vec3b>(i,j)[0]< *it + 5)
        {
          nwimg.at<Vec3b>(i,j)=img.at<Vec3b>(i,j);
        }
      }
    }
    curve_points.push_back(extract_points(nwimg,*it,ten_length));
    if(DEBUG == 2)
    {
      cvtColor(nwimg, nwimg, CV_HSV2BGR);
      imshow("curves",nwimg);waitKey(0);
    }
  }
  if(DEBUG == 3)
  {
    cvtColor(nwimg, nwimg, CV_HSV2BGR);
    imshow("curves",nwimg);
	  waitKey(0);
  }

	return curve_points;
}


int main(int argc, char *argv[])
{
  string inputFilename = argv[1];
  string outputFilename = argv[2];
  float xStart = atof(argv[3]);
  float xDelta = atof(argv[4]);
  int ten_length = atoi(argv[5]);
  float yStart = atof(argv[6]);
  float yDelta = atof(argv[7]);
  int yscale = atoi(argv[8]);

  Mat img;
  vector<int> a;
  // a.push_back(30);
  // a.push_back(94);
  // a.push_back(166);
  // a.push_back(178);
  // a.push_back(113);
  // a.push_back(52);
  int caller =0;
  if(argc == 9)
  {
    ;//cout<<"basic"<<endl;
  }
  else{
    for(int i=9;i<argc;++i)
      a.push_back(atoi(argv[i]));
    caller=1;
  }

  //namedWindow("original", CV_WINDOW_FULLSCREEN);
  //namedWindow("filtered", CV_WINDOW_NORMAL);
  img = imread(inputFilename, CV_LOAD_IMAGE_COLOR);
  vector<vector<Point> >curvePoints;
  //imshow("original",img);
  if(caller)
    curvePoints = findplot(img, a, ten_length);
  else
    curvePoints = findplot(img,ten_length);

  ofstream fout;
  fout.open(outputFilename.c_str(), ofstream::out);
  int numCurves = curvePoints.size();
  int numPoints = curvePoints[0].size();
  double actualx=0;
  double actualy=0;
  for(int i=0;i<numPoints;++i)//each iteration writes a row in the file
  {
    float x = curvePoints[0][i].x;
    actualx=double(xStart + double(double(xDelta / ten_length) * x));
    fout<<actualx<<" ";
    for(int j=0;j<numCurves;++j)
    {
      float y = curvePoints[j][i].y;
      if(y==-1)
        fout<<"- ";
      else
      {
        actualy=double(yStart + double(double(yDelta / yscale) * y));
        fout<<actualy<<" ";
      }
    }
    fout<<endl;
  }




  /*for(int i=0;i<numPoints;++i)//each iteration writes a row in the file
  {
    float x = curvePoints[0][i].x;
    actualx=double(xStart + double(double(xDelta / ten_length) * x));
    fout<<actualx<<" ";
  }
  fout<<endl;
  for(int j=0;j<numCurves;j++)
  {
    for(int i=0;i<numPoints;++i)//each iteration writes a row in the file
    {
      float y = curvePoints[j][i].y;
      actualy=double(yStart + double(double(yDelta / yscale) * y));
      fout<<actualy<<" ";
    }
    fout<<endl;
  }*/







  fout.close();
  //imshow("original",img);
  //findplot(img,a);
  //Return value of the above is a vector of a vector of Point.

}
