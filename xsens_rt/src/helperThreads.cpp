#include <iostream>
#include <chrono>
#include <thread>
#include "helperThreads.h"

void UserBreak::input_loop(void) {
	{
        using namespace std;
		while (!main_loop_end)
		{
			if (std::cin.get() == EOF) break;
			std::this_thread::sleep_for(10ms);
		}
		std::cout << std::endl
				  << "User input break" << std::endl;
		breaked = true;
	}
}

void SensorThread::gather_data()
{
	while (!main_loop_end)
	{
		i_ptr->get_data(&o);
   	    std::this_thread::sleep_for(sec_to_sleep);
		auto res = sec_to_sleep.count();
	}
}