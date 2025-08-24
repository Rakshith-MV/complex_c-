#include <stdio.h>
#include <stdlib.h>
#include<math.h>

#ifndef ANDROID
    #define EXPORT __attribute__((visibility("default")))
#endif

double trap(double*, int);
double multiply(double*, double*, int);
double simp(double*, int);

double function(double x, double y){
    return x*x + y*y;
}

typedef struct {
    double* values;
    double integral;
} output;


EXPORT void mfree(output* out){
    if(out){
        free(out->values);
        free(out);
    }
}

EXPORT output* trapezoidal(double* x, double* y, double (*func)(double, double), int length){
    output* out = malloc(sizeof(output));
    double *values = malloc(length * length * sizeof(double));
    for (int i = 0; i < length; i++) {
        for (int j = 0; j < length; j++) {
            values[i * length + j] = func(x[i], y[j]);
        }
    }
    double trapezoidal = trap(values, length);
    out->values = values;
    out->integral = trapezoidal;
    return out;
}

EXPORT output* simpsons(double* x, double* y, double (*func)(double, double), int length) {
    output* out = malloc(sizeof(output));
    double *values = malloc(length * length * sizeof(double));
    for (int i = 0; i < length; i++) {
        for (int j = 0; j < length; j++) {
            values[i * length + j] = func(x[i], y[j]);
        }
    }
    double simpsons =  simp(values, length);
    out->values = values;
    out->integral = simpsons;
    return out;
}


double trap(double* values, int length){
    double* matrix = malloc(length * length * sizeof(double));
    for(int i = 0; i < length; i++){
        for(int j = 0; j < length; j++){
            if(i == 0 || j == 0 || i == length-1 || j == length-1)
                matrix[i * length + j] = 2;
            else
                matrix[i * length + j] = 4;
        }
    }
    matrix[0] = 1;
    matrix[length-1] = 1;
    matrix[(length)*(length - 1)] = 1;
    matrix[(length)*(length) - 1] = 1;
    double temp = multiply(values, matrix, length);
    free(matrix);
    return temp;
}

double simp(double* values, int length){
    double matrix[9] = {1,4,1,4,16,4,1,4,1};
    double sum = 0;
    for(int i = 0; i < length; i++){
        for (int j=0; j < length; j++){
            if(i%2 == 1 && j%2 == 1){
                sum += multiply(values+(i-1)*length+(j-1), matrix, 3);
            }
        }
    }
    return sum;
}

double multiply(double* a, double* b, int length){
    double sum = 0;
    for(int i = 0; i<length; i++){
        for(int j = 0; j < length; j++){
            sum += (a[i * length + j] * b[i * length + j]);
        }
    }
    return sum;
}