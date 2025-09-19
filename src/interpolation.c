#include<math.h>
#include<stdlib.h>



#ifndef ANDROID
    #define EXPORT __attribute__((visibility("default")))
#endif

struct output{
    double* a;
    double* b;
    double* c;
};


EXPORT output* lagrage(double *x, double *y, int length){
    /*
    Lagrange interpolation polynomial.
    Inputs: x - array of x values
            y - array of y values
    Output: struct containing arrays a, b, c for the polynomial coefficients
    */
    for(int i = 0; i < length; i++){
        double (*func)(double);
        for(int j = 0; j < length; j++){
            if(i != j){
                
            }
        }
    }
}



EXPORT output* hermite(double* x, double* y, double* y1, int length, double xi){
    /*
    Hermite interpolation polynomial.
    Inputs: x - array of x values
            y - array of y values
            y1 - array of derivative values at each x
            length - length of the arrays
            xi - the point at which to evaluate the polynomial
    Output: the value of the Hermite polynomial at xi
    */
    
}