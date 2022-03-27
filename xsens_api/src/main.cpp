#include "xstypes/xstime.h"
#include "Xsens.h"
#include "pyInterface.h"
#include <iostream>
#include <iomanip>
#include <string>
#include <vector>
#include <cmath>
#include <cstdlib>
#include <thread>

// This must be defined before the first time that "gnuplot-iostream.h" is included.
#define GNUPLOT_ENABLE_PTY
#include "gnuplot-iostream.h"
typedef std::vector<std::pair<int64_t, float> > vecf;
using namespace std;

class UserBreak
{
private:
	bool breaked = false;
public:
	bool is_breaked() { return breaked; }

	void input_loop(void) {
		while(cin.get() != EOF || main_loop_end) {
			sleep(1);
		}
		cout<<endl<<"User input break"<<endl;
		breaked = true;
	}
	bool main_loop_end;
};


//--------------------------------------------------------------------------------
int main(void)
{
    Gnuplot angles;
	Gnuplot spd;
	Gnuplot coord;

	vecf lat; vecf lon; vecf roll; vecf pitch; vecf yaw; vecf ve; vecf vn;

	UserBreak ub;
	std::thread thread(&UserBreak::input_loop, &ub);
	//cout << string(79, '-') << endl;
	pyInterface i(57, 43, 100, 1);
	if (!i.ready()) {
		cout<< "Exit" <<endl;
		ub.main_loop_end = true;
		exit(-1);
	}
	OUT o{};
	int64_t startTime = XsTime::timeStampNow();
	int64_t now = XsTime::timeStampNow() - startTime;
	std::cout<<std::endl;
	while (1)
	{
		if (!i.is_data_avail()) continue;
		o = *(i.get_data());

		cout << setw(5) << fixed << setprecision(2);
		cout << "\r"
		<< "Lat:" << o.lat
		<< ", Lon:" << o.lon;

		cout 
		<< " |Roll:" << o.roll
		<< ", Pitch:" << o.pitch
		<< ", Yaw:" << o.yaw;

		cout 
		<< " |V_e:" << o.v_e 
		<< ", V_n:" << o.v_n;

		cout << flush;
		lat.push_back(make_pair(now, o.lat)); lon.push_back(make_pair(now, o.lon));
		roll.push_back(make_pair(now, o.roll)); pitch.push_back(make_pair(now, o.pitch)); yaw.push_back(make_pair(now ,o.yaw));
		ve.push_back(make_pair(now, o.v_e)); vn.push_back(make_pair(now, o.v_n));
		coord << "plot"
				<< coord.file1d(lat) << "with lines title 'lat',"
				<< coord.file1d(lon) << "with lines title 'lon'" << std::endl;

		spd << "plot"
				<< coord.file1d(ve) << "with lines title 've',"
				<< coord.file1d(vn) << "with lines title 'vn'" << std::endl;


		angles << "plot"
				<< angles.file1d(roll) << "with lines title 'roll',"
				<< angles.file1d(pitch) << "with lines title 'pitch',"
				<< angles.file1d(yaw) << "with lines title 'yaw'" << std::endl;

		XsTime::msleep(0);
		now = XsTime::timeStampNow() - startTime;
		if (ub.is_breaked()) break;
	}
	cout << "\n" << string(79, '-') << "\n";
	spd.clearTmpfiles();
	angles.clearTmpfiles();
	coord.clearTmpfiles();
	spd.close();
	ub.main_loop_end = true;
	thread.join();
	string s="pkill -9 -f gnuplot";
	system(s.c_str());
	exit(0);
}