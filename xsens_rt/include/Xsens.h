#ifndef Xsens_h__
#define Xsens_h__
#include "xsensdeviceapi.h"
#include "callbackHandler.h"
#include "vectors.h"

typedef struct
{
	vec_body acc;
	vec_body gyr;
	vec_body mag;
} SensData;

class Xsens
{
public:
	Xsens(uint16_t frequency=100, bool logdata = false);
	~Xsens();
	bool recieve(SensData *data);
	bool data_availible();
	void set_frequency(uint16_t freq) { frequency = freq; };
	int init();

private:
	int deinit();
	int handleError(std::string errorstr);
	int log();
	int scanDevice();
	int configureDevice();
	int openPort();

	XsDevice* device;
	XsControl* control;
	XsPortInfo mtPort;
	CallbackHandler callback;
	bool logdata;
	uint16_t frequency;
};


#endif