#include<math.h>
#include<stdlib.h>
// #include<stdio.h>

#ifndef ANDROID
    #define EXPORT __attribute__((visibility("default")))
#endif

// double RungeKutta(double*, double (*)(double, double), int, double);
// double func(double, double);
double* euler_first(double (*)(double, double), double, double, double, double);

typedef struct {
    double* values;
    double error;
} output;

EXPORT void mfree(double* out){
    free(out);
}


EXPORT double* euler_first(double (*func)(double, double), double x0, double xn, double y0, double h)
/*
Inputs: function, initial x, final x, initial y, step size
Outputs: array of y values at each step

The function is basically y' so we can use hermite interpolation to find the 
best fit.

Euler method for solving ordinary differential equations (ODEs).
dy/dx = f(x, y)
Theorem: Suppose D = {(t,y) : a <= t <= b, -infinity < y < infinity} and that
f(t,y) is continuous on D, and f is lipshitz continuous in y on D, then 
the ivp y'(t) = f(t,y), y(t0) = y0 has a unique solution on [a,b].
*/
{
    double* result = (double*)malloc(sizeof(double) * ( (int)((xn - x0) / h) + 1) );
    double a = x0;
    result[0] = y0;
    int n = 1;
    while(a <= xn){
        result[n] = result[n-1] + h * func(a, result[n-1]);
        a += h;
        n++;
    }
    return result;
}

EXPORT double* RungeKutta(double (*func)(double, double), double x0, double xn, double y0 , double h){
    int length = (int)((xn - x0) / h) + 1;
    double* y = (double*)malloc(length * sizeof(double));
    y[0] = y0; // initial condition
    double x = x0;
    for(int i = 1; i < length; i++){
        double k1 = h * func(x, y[i-1]);
        double k2 = h * func(x + h/2, y[i-1] + k1/2);
        double k3 = h * func(x + h/2, y[i-1] + k2/2);
        double k4 = h * func(x + h, y[i-1] + k3);
        y[i] = y[i-1] + (k1 + 2*k2 + 2*k3 + k4) / 6;
        x += h;
    }
    return y;

}


// double func(double x, double y){
//     return y - x*x + 1;
// }


// int main(){
//     double* result = RungeKutta(func, 0.0, 2.0, 0.5, 0.2);
//     free(result);
//     return 0;
// }