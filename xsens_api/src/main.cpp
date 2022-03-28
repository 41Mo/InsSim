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
typedef std::vector<float> vecf;
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

    coord << "set yrange [-180:180]\n set";
	angles << "set yrange [-360:360]\n";
	spd << "set yrange [-1:]\n";
	vecf lat; vecf lon; vecf roll; vecf pitch; vecf yaw; vecf ve; vecf vn;

	UserBreak ub;
	std::thread thread(&UserBreak::input_loop, &ub);
	cout << string(79, '-') << endl;
	pyInterface i(57, 43, 100, 1);
	if (!i.ready()) {
		cout<< "Exit" <<endl;
		ub.main_loop_end = true;
		exit(-1);
	}
	OUT o{};
	std::cout<<std::endl;
	while (1)
	{
		if (ub.is_breaked()) break;
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
		lat.push_back(o.lat); lon.push_back(o.lon);
		roll.push_back(o.roll); pitch.push_back(o.pitch); yaw.push_back(o.yaw);
		ve.push_back(o.v_e); vn.push_back(o.v_n);

        coord << "plot"
		 	<< "'-' binary" << coord.binFmt1d(lat, "array") << "with lines title 'lat', "
			<< "'-' binary" << coord.binFmt1d(lon, "array") << "with lines title 'lon'\n";
        angles << "plot"
		 	<< "'-' binary" << coord.binFmt1d(roll, "array") << "with lines title 'roll', "
			<< "'-' binary" << coord.binFmt1d(pitch, "array") << "with lines title 'pitch', "
			<< "'-' binary" << coord.binFmt1d(yaw, "array") << "with lines title 'yaw'\n";
		spd << "plot"
		 	<< "'-' binary" << coord.binFmt1d(ve, "array") << "with lines title 'v_e', "
			<< "'-' binary" << coord.binFmt1d(vn, "array") << "with lines title 'v_n'\n";

        coord.sendBinary1d(lat); coord.sendBinary1d(lon); coord.flush();
		angles.sendBinary1d(roll); angles.sendBinary1d(pitch); angles.sendBinary1d(yaw); angles.flush();
		spd.sendBinary1d(ve); spd.sendBinary1d(vn); spd.flush();

		XsTime::msleep(0);
	}
	cout << "\n" << string(79, '-') << "\n";
	ub.main_loop_end = true;
	thread.join();
	string s="pkill -9 -f gnuplot";
	system(s.c_str());
	i.~pyInterface();
	exit(0);
}