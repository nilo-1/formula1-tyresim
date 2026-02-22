#include<iostream>
#include<cmath>
#include<iomanip>
using namespace std;
int timeFormat(double t)
{
 int Minutes,Seconds,Millis;
 Minutes=(int)t / 60;
 Seconds=(int)t%60;
 Millis = round((t - (int)t) * 1000);
 cout << Minutes << ":" << std::setfill('0') << std::setw(2) << Seconds << ":" << std::setfill('0') << std::setw(3) << Millis;
 return 0;
}
