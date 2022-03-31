#include <iostream>
#include <iomanip>
#include <string>
#include <vector>
#include <cmath>
#include <cstdlib>
#include <thread>
#include <chrono>

#include "TCanvas.h"
#include "TGraph.h"
#include "TApplication.h"
#include "TAxis.h"
#include "xstypes/xstime.h"
#include "Xsens.h"
#include "pyInterface.h"
#include "helperThreads.h"

using namespace std::chrono_literals;
using namespace std;

static const uint8_t plt_number = 13;
static const char *deg_label = "deg";
static const char *vel = "m/s";
static const char *time_label = "time, sec";
std::vector<std::shared_ptr<TGraph>> plots;
std::array<uint8_t, plt_number> p_w_pos{{1,2,3,4,5,7,8,10,11,12,13,14,15}}; // plot position in root window
//--------------------------------------------------------------------------------
int main(int argc, char* argv[])
{
	TApplication rootapp("spectrum", &argc, argv);

	auto c1 = std::make_shared<TCanvas>("c1", "");
	c1->SetWindowSize(1920, 1080);
	// divide the canvas into seven vertical sub-canvas
	c1->Divide(3, 5);
	
	for (uint8_t i = 0; i<plt_number; i++) {
		plots.push_back(std::make_shared<TGraph>(1));
		if (i<3) {
			plots.at(i)->GetXaxis()->SetTitle(time_label);
			plots.at(i)->GetYaxis()->SetTitle(deg_label);
			if (i == 0) plots.at(i)->SetTitle("roll");
			if (i == 1) plots.at(i)->SetTitle("pitch");
			if (i == 2) plots.at(i)->SetTitle("yaw");
		} else if (i<5) {
			plots.at(i)->GetXaxis()->SetTitle(time_label);
			plots.at(i)->GetYaxis()->SetTitle(deg_label);
			if (i == 3) plots.at(i)->SetTitle("lat");
			if (i == 4) plots.at(i)->SetTitle("lon");
		} else if (i<7) {
			plots.at(i)->GetXaxis()->SetTitle(time_label);
			plots.at(i)->GetYaxis()->SetTitle(vel);
			if (i == 5) plots.at(i)->SetTitle("v_e");
			if (i == 6) plots.at(i)->SetTitle("v_n");
		}
		c1->cd(p_w_pos[i]);
		plots.at(i)->Draw();
	}
	cout << "Input frequency, alignment time in seconds" << endl;
	uint16_t frq;
	uint64_t time;
	cin >> frq >> time;
	//55.7558, 37.6173
	auto i_p = make_shared<pyInterface>(57.765,37.685, frq, time);
	UserBreak ub;
	SensorThread st(i_p);
	std::thread ui_thread(&UserBreak::input_loop, &ub);
	std::thread se_thread(&SensorThread::gather_data, &st);
	std::cout << std::string(79, '-') << std::endl;

	if (!i_p->ready()) {
		std::cout<< "Exit" <<std::endl;
		ub.main_loop_end = true;
		exit(-1);
	}


	uint64_t point_num = 0;
	int64_t startTime = XsTime::timeStampNow();
	auto t1 = std::chrono::high_resolution_clock::now();
	while (1)
	{
		if (ub.is_breaked()) break;
		auto o = st.o;
		for (uint8_t i = 0; i<plt_number; i++) {
			plots.at(i)->SetPoint(point_num, XsTime::timeStampNow() - startTime, o.data[i]);
			c1->cd(p_w_pos[i]);
			c1->Update();
			c1->Pad()->Draw();
		}
		point_num++;

		print_sens_data(o);

    	auto t2 = std::chrono::high_resolution_clock::now();
    	auto diff = t2 - t1;
    	if(diff < 16ms)
    	    std::this_thread::sleep_for(16ms - diff);
    	t1 = t2;
	}

	std::cout << "\n" << std::string(79, '-') << "\n";
	ub.main_loop_end = true;
	st.main_loop_end = true;
	se_thread.join();
	ui_thread.join();
	i_p->~pyInterface();
	exit(0);
}
