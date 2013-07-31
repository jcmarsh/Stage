#include <math.h>

// Hopefully a correct implementation of the Box-Muller Transform
double Noise_Get_Normalized(double scalar) {
  double u_0, u_1, z_0;

  u_0 = rand() / (double)RAND_MAX;
  u_1 = rand() / (double)RAND_MAX;

  z_0 = sqrt(-2 * log(u_0)) * cos(2 * M_PI * u_1);
  // Only need one value, so z_1 is not calculated
  return z_0;
}
