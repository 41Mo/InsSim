#ifndef analysis_api_h__
#define analysis_api_h__

#include "nav_alg.h"

#ifdef __cplusplus
extern "C" {
#endif

struct SENSORS
{
    vec_body *acc;
    vec_body *gyr;
    uint64_t size;
};



class Analysis_api
{
private:
    /* data */
    uint64_t points;
    SENSORS sensors;
    Nav nav{};
public:
    Analysis_api(
        SENSORS sens,
        float roll, float pitch, float yaw,
        float lat, float lon,
        int frequency, uint64_t time
    );
    ~Analysis_api();
    void loop();
};

#ifdef __cplusplus
}
#endif

#endif