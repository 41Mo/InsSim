#ifndef pyInterface_h__
#define pyInterface_h__

#include "nav_alg.h"
#include "vectors.h"
#include "constants.h"
#include "Xsens.h"

class NavOut
{
  public:
    float roll()  { return data[0]; };
    float pitch() { return data[1]; };
    float yaw()   { return data[2]; };
    float lat()   { return data[3]; };
    float lon()   { return data[4]; };
    float v_e()   { return data[5]; };
    float v_n()   { return data[6]; };

    void roll(float r)  {  data[0] = r; };
    void pitch(float p) {  data[1] = p; };
    void yaw(float y)   {  data[2] = y; };
    void lat(float l)   {  data[3] = l; };
    void lon(float l)   {  data[4] = l; };
    void v_e(float v)   {  data[5] = v; };
    void v_n(float v)   {  data[6] = v; };
    void ax(float a)    {  data[7] = a; };
    void ay(float a)    {  data[8] = a; };
    void az(float a)    {  data[9] = a; };
    void gx(float g)    {  data[10]= g; };
    void gy(float g)    {  data[11]= g; };
    void gz(float g)    {  data[12]= g; };
    float data[13]{0};
};

  class pyInterface
  {
  private:
    /* data */
    //NavOut data{};
    Nav nav{};
    Xsens xsens{};
    SensData sens{};
    void alignment(int64_t time);
	  bool error = false;

  public:
    pyInterface(float lat, float lon, uint16_t frq = 100, int64_t alignment_time = 60);
    ~pyInterface();
    bool ready() { return !error; }
    //bool is_data_avail();
    void get_data(NavOut *o);
  };

void print_sens_data(NavOut o);
#endif