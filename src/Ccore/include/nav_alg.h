#include "vectors.h"
#include <stdint.h>

class Nav {
public:
    // constructor
    Nav();
    // destructor
    ~Nav() {};

	void puasson_equation();
	void euler_angles();
	void acc_body_enu();
	void speed();
	void coordinates();
	void ang_velocity_body_enu();
	void aligment(float roll, float pitch, float yaw);
	void iter(vec_body acc, vec_body gyr);
	void init(float phi, float lambda, int frequency);
private:
	// Earth constants
	const float R{6378245.0};
	const float U{((3.14 * 15) / 180) / 3600}; // ((Pi * Wspd_earth)) / 180 degree
	const float G{9.81};

	// variables
	float c11{0}, c12{0}, c13{0}, c21{0}, c22{0}, c23{0}, c31{0}, c32{0}, c33{0}; //начальные элементы матрицы

	float H{0};
	float teta{0};
	float gamma{0};
	float psi{0};

	vec_body w_body {0, 0, 0};
	vec_body a_body {0, 0, 0};
	vec_enu v_enu {0, 0, 0};

	// uninitialized variables
	float phi;
	float lambda;
	int frequency;
	float dt;
	vec_enu w_enu;
	vec_enu a_enu;
};