#ifndef pyInterface_h__
#define pyInterface_h__

#include "nav_alg.h"
#include "vectors.h"
#include "constants.h"
#include "Xsens.h"

typedef struct
{
  float roll;
  float pitch;
  float yaw;
  float lat;
  float lon;
  float v_e;
  float v_n;
} OUT;

  class pyInterface
  {
  private:
    /* data */
    OUT data{};
    Nav nav{};
    Xsens xsens{};
    SensData sens{};
    void alignment(int64_t time);
	  bool error = false;

  public:
    pyInterface(float lat, float lon, uint16_t frq = 100, int64_t alignment_time = 60);
    ~pyInterface();
    bool ready() { return !error; }
    bool is_data_avail();
    OUT *get_data() { return &data; }
  };

#endif