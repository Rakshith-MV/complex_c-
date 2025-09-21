#include<math.h>
#include<stdlib.h>

#ifndef ANDROID
    #define EXPORT __attribute__((visibility("default")))
#endif

// double* RungeKutta(double (*)(double, double), double, double, double, double);
// double func(double, double);
// double* euler_first(double (*)(double, double), double, double, double, double);


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

EXPORT double* RungeKutta2( double(*func)(double, double, double),double x0, double xn, double y0,double dy0, double h){
    int length = (int)((xn - x0) / h) + 1;
    double* y = (double*)malloc( 2* length * sizeof(double));
    y[0] = y0; // initial condition
    y[length]= dy0;
    double x = x0;
    for(int i = 1; i < length; i++){
        double k1 = h * y[length + i -1];
        double l1 = h * func(x, y[i-1], y[length+i-1]);    
        double k2 = h * (y[length+i-1] + l1/2);
        double l2 = h * func(x + h/2, y[i-1] + k1/2, y[length+i-1] + l1/2);
        double k3 = h * (y[length+i-1] + l2/2);
        double l3 = h * func(x + h/2, y[i-1] + k2/2, y[length+i-1] + l2/2);
        double k4 = h * (y[length+i-1] + l3);
        double l4 = h * func(x + h, y[i-1] + k3, y[length+i-1] + l3);  
        y[i] = y[i-1] + (k1 + 2*k2 + 2*k3 + k4) / 6;
        y[length+i] = y[length+i-1] + (l1 + 2*l2 + 2*l3 + l4) / 6;
        x += h;
    }
    return y;
}