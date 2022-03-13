#include "vectors.h"

class Nav {
public:
    //constructor
    Nav() {};
    // destructor
    ~Nav() {};

	void puasson_equation();
	void euler_angles();
	void acc_body_enu();
	void speed();
	void coordinates();
	void ang_velocity_body_enu();
	float arithmetic_mean(float data[], int size);
	void aligment(float acc_x[], float acc_y[], float acc_z[], float heading, int size);
private:
	//Earth Parameters
	const float R = 6378245.0;
	const float U = ((3.14 * 15) / 180) / 3600; // ((Pi * Wspd_earth)) / 180 degree
	const float G = 9.81;

	//Input values
	float frequency = 10;
	float dt = 1/frequency;

	//Default values
	float c11 = 0, c12 = 0, c13 = 0, c21 = 0, c22 = 0, c23 = 0, c31 = 0, c32 = 0, c33 = 0; //начальные элементы матрицы
	float phi = 0;
	float lambda = 0;
	float H = 0;
	vec_body w_body = {0, 0, 0};
	vec_body a_body = {0, 0, 0};
	vec_enu v_enu = {0, 0, 0};

	//Local variables
	vec_enu w_enu = {0, 0, 0};
	vec_enu a_enu = {0, 0, 0};
	float teta = 0;
	float gamma = 0;
	float psi = 0;
};