#include "pyInterface.h"
#include "Xsens.h"
#include <iostream>
#include <iomanip>

/**
 * Convert the angle given in radians to degrees.
 */
template<typename F>
F rad2deg(F angle) {
    return angle * 180.0 / M_PI;
}

/**
 * Convert the angle given in radians to degrees.
 */
template<typename F>
F deg2rad(F angle) {
    return angle * M_PI / 180.0;
}


pyInterface::pyInterface(float lat, float lon, uint16_t frq, int64_t alignmentTime){
    xsens.set_frequency(frq);
    if (xsens.init() !=0) error = true;
    nav.init(deg2rad(lat), deg2rad(lon), frq);
    if (ready()) alignment(alignmentTime);
}

pyInterface::~pyInterface(){
}

void pyInterface::alignment(int64_t time) {
    int measCount = 0;
    SensData s{};
    SensData mean{};

    std::cout << "stating alignment for amount of " << time << " sec\n";
    time *= 1000;
	int64_t startTime = XsTime::timeStampNow();
	std::cout << std::setw(5) << std::fixed << std::setprecision(2);
    auto now = XsTime::timeStampNow() - startTime;
	while (now <= time) {
	    if (xsens.data_availible()) {
	    	if (xsens.recieve(&s)) {
                mean.acc.X += s.acc.X;
                mean.acc.Y += s.acc.Y;
                mean.acc.Z += s.acc.Z;

                mean.mag.X += s.mag.X;
                mean.mag.Y += s.mag.Y;
                mean.mag.Z += s.mag.Z;
                measCount++;
		        std::cout << "\r" << now << std::flush;
           }
       }
       now = XsTime::timeStampNow() - startTime;
    }
    std::cout<<std::endl;

    mean.acc.X /= measCount;
    mean.acc.Y /= measCount;
    mean.acc.Z /= measCount;
    mean.mag.X /= measCount;
    mean.mag.Y /= measCount;

    float yaw = atan2f(mean.mag.X, mean.mag.Y);
    nav.alignment(mean.acc.X, mean.acc.Y, mean.acc.Z, yaw);
}

void pyInterface::get_data(NavOut *data) {
	if (xsens.data_availible()) {
		if (xsens.recieve(&sens)) {
            nav.iter(sens.acc, sens.gyr);

            data->roll(rad2deg(nav.gamma));
            data->pitch(rad2deg(nav.teta));
            data->yaw(rad2deg(nav.psi));
            data->lat(rad2deg(nav.phi));
            data->lon(rad2deg(nav.lambda));
            data->v_e(nav.v_enu.E);
            data->v_n(nav.v_enu.N);
            data->ax(sens.acc.X);
            data->ay(sens.acc.Y);
            data->az(sens.acc.Z);
            data->gx(sens.gyr.X);
            data->gy(sens.gyr.Y);
            data->gz(sens.gyr.Z);
        }
    }
}