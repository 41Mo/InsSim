#ifndef HELPER_THREADS_H
#define HELPER_THREADS_H

#include "pyInterface.h"
class UserBreak
{
private:
	bool breaked = false;

public:
	bool is_breaked() { return breaked; }
	void input_loop(void);

	bool main_loop_end;
};

class SensorThread
{
public:
	bool main_loop_end;
	NavOut o{};
	SensorThread(std::shared_ptr<pyInterface> i, int32_t freq) : i_ptr(i)
	{
		using namespace std::chrono_literals;
		sec_to_sleep = std::chrono::milliseconds(1000/freq);
	}
	void gather_data();

private:
	std::shared_ptr<pyInterface> i_ptr;
	std::chrono::milliseconds sec_to_sleep;
};

#endif
