#include <iostream>
#include <vector>
#include <thread>
#include <chrono>

#include "TCanvas.h"
#include "TGraph.h"
#include "TApplication.h"
#include "TAxis.h"
#include "Xsens.h"
#include "pyInterface.h"
#include "helperThreads.h"

static const uint8_t plt_number = 7;
static const char *deg_label = "deg";
static const char *vel = "m/s";
static const char *time_label = "time, sec";
std::vector<std::shared_ptr<TGraph>> plots;
std::array<uint8_t, plt_number> p_w_pos{{1, 2, 3, 4, 5, 7, 8 /*,10,11,12,13,14,15*/}}; // plot position in root window
//--------------------------------------------------------------------------------
int main(int argc, char *argv[])
{
	using namespace std::chrono_literals;
	using namespace std::chrono;
	using namespace std;


	auto i_p = make_shared<pyInterface>();
	//check if xsens dev is present
	if (i_p->scan_dev() != 0) exit(0);
	// setup xsens device, setup nav_alg
	cout << "Input frequency, alignment time in seconds" << endl;
	uint16_t frq;
	uint64_t time;
	cin >> frq >> time;
	if (frq < 10 || time < 0)
	{
		cout << "Wrong input\n";
		exit(-1);
	}
	i_p->init(57.765, 37.685, frq);
	if (!i_p->ready())
	{
		std::cout << "Exit" << std::endl;
		exit(-1);
	}

	if (time != 0)
	{
		i_p->alignment(time);
	}
	else
	{
		cout << "Skipping alignment;\n";
	}

	// setup root app
	TApplication rootapp("spectrum", &argc, argv);

	auto c1 = std::make_shared<TCanvas>("c1", "");
	c1->SetWindowSize(1920, 700);
	// divide the canvas into seven vertical sub-canvas
	c1->Divide(3, 3);

	for (uint8_t i = 0; i < plt_number; i++)
	{
		plots.push_back(std::make_shared<TGraph>(1));
		if (i < 3)
		{
			plots.at(i)->GetXaxis()->SetTitle(time_label);
			plots.at(i)->GetYaxis()->SetTitle(deg_label);
			if (i == 0)
				plots.at(i)->SetTitle("roll");
			if (i == 1)
				plots.at(i)->SetTitle("pitch");
			if (i == 2)
				plots.at(i)->SetTitle("yaw");
		}
		else if (i < 5)
		{
			plots.at(i)->GetXaxis()->SetTitle(time_label);
			plots.at(i)->GetYaxis()->SetTitle(deg_label);
			if (i == 3)
				plots.at(i)->SetTitle("lat");
			if (i == 4)
				plots.at(i)->SetTitle("lon");
		}
		else if (i < 7)
		{
			plots.at(i)->GetXaxis()->SetTitle(time_label);
			plots.at(i)->GetYaxis()->SetTitle(vel);
			if (i == 5)
				plots.at(i)->SetTitle("v_e");
			if (i == 6)
				plots.at(i)->SetTitle("v_n");
		}
		c1->cd(p_w_pos[i]);
		plots.at(i)->Draw();
	}

	// create sensor reader and user input reader threads
	UserBreak ub;
	SensorThread st(i_p, frq);
	std::thread ui_thread(&UserBreak::input_loop, &ub);
	std::thread se_thread(&SensorThread::gather_data, &st);

	// delay plotting for 1s. We need to gather sens data first
	std::this_thread::sleep_for(std::chrono::seconds(1));

	uint64_t point_num = 0; // plots starting point, should be zero

	// time, when we started calulations
	auto startTime = high_resolution_clock::now();
	auto t1 = high_resolution_clock::now();
	std::cout << std::string(79, '-') << std::endl;

	while (1)
	{
		if (ub.is_breaked())
			break; // break loop on user input
		for (uint8_t i = 0; i < plt_number; i++)
		{
			// get data from sensor thread, and set it as a point with time from start
			auto nanosec = (high_resolution_clock::now() - startTime).count();
			auto t_from_start = nanosec * 10e-9;
			plots.at(i)->SetPoint(point_num, t_from_start, st.o.data[i]);
			// update plots
			c1->cd(p_w_pos[i]);
			c1->Update();
			c1->Pad()->Draw();
		}
		point_num++;

		print_sens_data(st.o); // print data in console

		auto t2 = std::chrono::high_resolution_clock::now();
		auto diff = t2 - t1; // calculate diff between loop start and end.
		if (diff < 16ms)	 // prevent thread updating faster then then 16ms <=>60FPS
			std::this_thread::sleep_for(16ms - diff);
		t1 = t2;
	}
	std::cout << "\n"
			  << std::string(79, '-') << "\n";

	// stop other threads
	ub.main_loop_end = true;
	st.main_loop_end = true;
	se_thread.join();
	ui_thread.join();
	i_p->~pyInterface();
	exit(0);
}
