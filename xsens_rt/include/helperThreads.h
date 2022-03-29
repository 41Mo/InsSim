#include <iostream>
#include <memory>
#include <chrono>
#include <cstdlib>
#include "pyInterface.h"
using namespace std::chrono_literals;
class UserBreak
{
private:
	bool breaked = false;
public:
	bool is_breaked() { return breaked; }

	void input_loop(void) {
		while(std::cin.get() != EOF || main_loop_end) {
    	    std::this_thread::sleep_for(500ms);
		}
		std::cout<<std::endl<<"User input break"<<std::endl;
		breaked = true;
	}
	bool main_loop_end;
};

class SensorThread
{
	public:
	bool main_loop_end;
		NavOut o{};
		SensorThread(std::shared_ptr<pyInterface> i) {
			i_ptr = i;
		}
		void gather_data() {
			while (!main_loop_end) {
				i_ptr->get_data(&o);
			} 
		}
	private:
	std::shared_ptr<pyInterface> i_ptr;
};

void print_sens_data(NavOut o) {
	std::cout << std::setw(5) << std::fixed << std::setprecision(2);
	std::cout << "\r"
	<< "Lat:" << o.lat()
	<< ", Lon:" << o.lon();
	std::cout 
	<< " |Roll:" << o.roll()
	<< ", Pitch:" << o.pitch()
	<< ", Yaw:" << o.yaw();
	std::cout 
	<< " |V_e:" << o.v_e()
	<< ", V_n:" << o.v_n();
	std::cout << std::flush;
}