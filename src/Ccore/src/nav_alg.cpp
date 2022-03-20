#include <math.h>
#include "nav_alg.h"

Nav::Nav()
{
}

void Nav::init(float phi, float lambda, int frequency) {
	Nav::phi = phi;
	Nav::lambda = lambda;
	Nav::frequency = frequency;
	dt = 1/frequency;
}

void Nav::puasson_equation() 
{
	c11 = c11 - dt * (c13 * w_body.Y + c31 * w_enu.N - c12 * w_body.Z - c21 * w_enu.U);
	c12 = c12 + dt * (c13 * w_body.X - c32 * w_enu.N - c11 * w_body.Z + c22 * w_enu.U);
	c13 = c13 - dt * (c12 * w_body.X - c11 * w_body.Y + c33 * w_enu.N - c23 * w_enu.U);
	c21 = c21 + dt * (c31 * w_enu.E - c23 * w_body.Y + c22 * w_body.Z - c11 * w_enu.U);
	c22 = c22 + dt * (c23 * w_body.X + c32 * w_enu.E - c21 * w_body.Z - c12 * w_enu.U);
	c23 = c23 - dt * (c22 * w_body.X - c33 * w_enu.E - c21 * w_body.Y + c13 * w_enu.U);
	c31 = c31 - dt * (c21 * w_enu.E + c33 * w_body.Y - c11 * w_enu.N - c32 * w_body.Z);
	c32 = c32 + dt * (c33 * w_body.X - c22 * w_enu.E + c12 * w_enu.N - c31 * w_body.Z);
	c33 = c33 - dt * (c32 * w_body.X + c23 * w_enu.E - c31 * w_body.Y - c13 * w_enu.N);
}

void Nav::euler_angles()
{
	float c0 = sqrt(pow(c13, 2) + pow(c33, 2));
	teta = atan(c23 / c0);
	gamma = -atan(c13 / c33);
	psi = atan(c21 / c22);
}

void Nav::acc_body_enu()
{
	a_enu.E = c11 * a_body.X + c12 * a_body.Y + c13 * a_body.Z;
	a_enu.N = c21 * a_body.X + c22 * a_body.Y + c23 * a_body.Z;
	a_enu.U = c31 * a_body.X + c32 * a_body.Y + c33 * a_body.Z;
}

void Nav::speed()
{
	v_enu.E = v_enu.E + (a_enu.E + (U * sin(phi) + w_enu.U) * v_enu.N) * dt;
	v_enu.N = v_enu.N + (a_enu.N + (U * sin(phi) + w_enu.U) * v_enu.E) * dt;

}

void Nav::coordinates()
{
	// Latitude
	phi = phi + (v_enu.N / (R + H)) * dt;
	// Longitude
	lambda = lambda + (v_enu.E / ((R + H) * cos(phi))) * dt;

}

void Nav::ang_velocity_body_enu()
{
	w_enu.E = -v_enu.N / (R + H);
	w_enu.N = v_enu.E / (R + H) + U * cos(phi);
	w_enu.U = (v_enu.E / (R + H)) * tan(phi) + U * sin(phi);
}

void Nav::aligment(float roll, float pitch, float yaw)
{
	float psi = yaw;
	float teta = pitch;
	float gamma = roll;
	
	float sp = sin(psi); float st = sin(teta); float sg = sin(gamma);
	
	float cp = cos(psi); float ct = cos(teta); float cg = cos(gamma);
	
	c11 = cp * cg + sp * st * sg;
	c12 = sp * ct;
	c13 = cp * sg - sp * st * cg;
	c21 = - sp * cg + cp * st * sg;
	c22 = cp * ct;
	c23 = - sp * sg - cp * st * cg;
	c31 = - ct * sg;
	c32 = st;
	c33 = ct * cg;
}

void Nav::iter(vec_body acc, vec_body gyr)
{
	w_body = gyr;
	a_body = acc;
	acc_body_enu();
	speed();
	ang_velocity_body_enu();
	puasson_equation();
	euler_angles();
	coordinates();
}
