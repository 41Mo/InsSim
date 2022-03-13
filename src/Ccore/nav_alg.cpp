#include <iostream>
#include <cmath>
using namespace std;


class nav_alg {


	struct vec_body //Matrix of a body 3-sided
	{
		float X;
		float Y;
		float Z;
	};
	struct vec_enu //The matrix of the geographical 3-sided
	{
		float E;
		float N;
		float U;
	};

private:
	//Earth Parameters
	const float R = 6378245.0;
	const float U = ((3.14 * 15) / 180) / 3600; // ((Pi * Wspd_earth)) / 180 degree
	const float G = 9.81;

	//Arithmetic mean function
	float arithmetic_mean(float data[], int size)
	{
		float sum = 0;
		for (int i = 0; i < size; ++i)
		{
			sum += data[i];
		}
		return sum / size;
	}

public:
	//Input values
	float frequency = 10;
	float dt = 1/frequency;

	//Default values
	float c11 = 0, c12 = 0, c13 = 0, c21 = 0, c22 = 0, c23 = 0, c31 = 0, c32 = 0, c33 = 0; //Initial elements of the matrix
	float phi = 0;
	float lambda = 0;
	float H = 0;
	vec_body w_body;
	vec_body a_body;
	vec_enu v_enu;

	//Local variables
	vec_enu w_enu;
	vec_enu a_enu;
	float teta = 0;
	float gamma = 0;
	float psi = 0;
	
		//Output values
		float spd_e[8];
		float spd_n[8];
		float pitch[8];
		float roll[8];
		float yaw[8];
		float lat[8];
		float lon[8];
		float a_e[8];
		float a_n[8];
		float a_u[8];
		float w_e[8];
		float w_n[8];
		float w_u[8];
	

		void _puasson_equation() 
		{
			c11 = c11 - dt * (c13 * w_body.Y + c31 * w_enu.N - c12 * w_body.Z - c21 * w_enu.U);
			c12 = c12 + dt * (c13 * w_body.X - c32 * w_enu.N - c11 * w_body.Z + c22 * w_enu.U);
			c13 = c13 - dt * (c12 * w_body.X - c11 * w_body.Y + c33 * w_enu.N - c23 * w_enu.U);
			c21 = c21 + dt * (c31 * w_enu.E - c23 * w_body.Y + c22 * w_body.Z - c11 * w_enu.U);
			c22 = c22 + dt * (c23 * w_body.X + c32 * w_enu.E - c21 * w_body.Z - c12 * w_enu.U);
			c23 = c23 - dt * (c22 * w_body.X - c33 * w_enu.E - c21 * w_body.Y + c13 * w_enu.U);
			c31 = c12 * c23 - c22 * c13;	//c31 - dt * (c21 * w_enu.E + c33 * w_body.Y - c11 * w_enu.N - c32 * w_body.Z);
			c32 = -(c11 * c23 - c21 * c13);	//c32 + dt * (c33 * w_body.X - c22 * w_enu.E + c12 * w_enu.N - c31 * w_body.Z);
			c33 = c11 * c22 - c21 * c13;	//c33 - dt * (c32 * w_body.X + c23 * w_enu.E - c31 * w_body.Y - c13 * w_enu.N);

		}

		void _euler_angles()
		{
			float c0 = sqrt(pow(c13, 2) + pow(c33, 2));
			teta = atan(c23 / c0);
			gamma = -atan(c13 / c33);
			psi = atan(c21 / c22);
		}

		void _acc_body_enu()
		{
			a_enu.E = c11 * a_body.X + c12 * a_body.Y + c13 * a_body.Z;
			a_enu.N = c21 * a_body.X + c22 * a_body.Y + c23 * a_body.Z;
			a_enu.U = c31 * a_body.X + c32 * a_body.Y + c33 * a_body.Z;
		}

		void _speed()
		{
			v_enu.E = v_enu.E + (a_enu.E + (U * sin(phi) + w_enu.U) * v_enu.N) * dt;
			v_enu.N = v_enu.N + (a_enu.N + (U * sin(phi) + w_enu.U) * v_enu.E) * dt;

		}
		void _coordinates()
		{
			//Latitude
			phi = phi + (v_enu.N / (R + H)) * dt;
			//Longitude
			lambda = lambda + (v_enu.E / ((R + H) * cos(phi))) * dt;

		}

		void _ang_velocity_body_enu()
		{
			w_enu.E = -v_enu.N / (R + H);
			w_enu.N = v_enu.E / (R + H) + U * cos(phi);
			w_enu.U = (v_enu.E / (R + H)) * tan(phi) + U * sin(phi);
		}


		void aligment(float acc_x[], float acc_y[], float acc_z[], float heading, int size)
		{
			float ax_mean = arithmetic_mean(acc_x, size);
			float ay_mean = arithmetic_mean(acc_y, size);
			float az_mean = arithmetic_mean(acc_z, size);

			float psi = heading;

			float sp = sin(psi);
			float st = ay_mean / G;
			float sg = -1 * ax_mean / sqrt(pow(ax_mean, 2) + pow(az_mean, 2));

			float cp = cos(psi);
			float ct = sqrt(pow(ax_mean, 2) + pow(az_mean, 2)) / G;
			float cg = az_mean / sqrt(pow(ax_mean, 2) + pow(az_mean, 2));

			float a11 = cp * cg + sp * st * sg;
			float a12 = sp * ct;
			float a13 = cp * sg - sp * st * cg;
			float a21 = - sp * cg + cp * st * sg;
			float a22 = cp * ct;
			float a23 = - sp * sg - cp * st * cg;
			float a31 = - ct * sg;
			float a32 = st;
			float a33 = ct * cg;
		}
		
};
