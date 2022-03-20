#include "analysis_api.h"

Analysis_api::Analysis_api(
    SENSORS sens,
    float roll, float pitch, float yaw,
    float lat, float lon,
    int frequency, uint64_t time
):
sensors(sens)
{
    points = time*frequency;
    nav.init(lat, lon, frequency);
    nav.aligment(roll, pitch, yaw);
}

void Analysis_api::loop() {
    for (uint64_t i = 0; i < points; i++)
    {
        nav.iter(sensors.gyr[i], sensors.acc[i]);
    }
}

Analysis_api::~Analysis_api()
{
}
