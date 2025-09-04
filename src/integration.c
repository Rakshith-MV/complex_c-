// #include<stdio.h>
#include<math.h>
#include<stdlib.h>


#ifndef ANDROID
    #define EXPORT __attribute__((visibility("default")))
#endif

double trap(double*, int, int);
double multiply(double*, double*, int);
double simp(double*, int, int);
// double function(double, double);
double roundn(double , int );


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

EXPORT output* trapezoidal1d(double* x, double (*func)(double), int length){
    output* out = malloc(sizeof(output));
    double *values = malloc(length * sizeof(double));
    double sum = 0.0;
    for (int i = 0; i < length; i++) {
        values[i] = roundn(func(x[i]), 5);
        sum = sum + 2*values[i];   
    }
    sum = sum - (values[0] + values[length-1]);
    sum = sum * (x[1] - x[0]) / 2;
    out->values = values;
    out->integral = sum;
    return out;
}

EXPORT output* simpsons1d(double* x, double (*func)(double), int length){
    output* out = malloc(sizeof(output));
    double *values = malloc(length * sizeof(double));
    int i = 1;
    double sum = 0.0;
    while(i < length-1){
        if(i % 2 == 0){
            values[i] = roundn(func(x[i]),5);
            sum += 2*values[i];
        }
        else{
            values[i] = roundn(func(x[i]),5);
            sum += 4*values[i];
        }
        i++;
    }
    values[0] = roundn(func(x[0]),5);
    values[length-1] = roundn(func(x[length-1]),5);
    sum += values[0] + values[length-1];
    sum *= (x[1] - x[0]) / 3;
    out->values = values;
    out->integral =  sum;
    return out;
}

EXPORT output* simpsons381d(double* x, double (*func)(double), int length){
    output *out = malloc(sizeof(output));
    double *values = malloc(length* sizeof(double));
    int j = 0;
    double sum = 0;
    for(int i = 0; i<length; i++){
        values[i] = roundn(func(x[i]),5);
    }
    while(j < length-1){             // why length -1 ???
        sum  += values[j] + 3*values[j+1] + 3*values[j+2] + values[j+3];
        j = j+3;
    }
    out->values = values;
    out->integral = 3*(x[1]-x[0])*sum/8;
    return out;
}

EXPORT output* gaussian(double (*func)(double), double a, double b){
    output *out = malloc(sizeof(output));
    double two_points, three_points = 0;
    double c = (b - a)/2;
    double d = (b+a)/2;
    two_points = c * (func(-c / sqrt(3) + d) + func(c / sqrt(3) + d));
    three_points = c * ( (5.0/9.0) * func(-c * sqrt(3.0/5.0) + d) + (8.0/9.0) * func(d) + (5.0/9.0) * func(c * sqrt(3.0/5.0) + d) );
    out->integral = two_points;
    out->values = malloc(sizeof(double));
    out->values[0] = three_points;
    return out;
}      


// ============================================================================================
EXPORT output* trapezoidal2d(double* x, double* y, double (*func)(double, double), int xlength, int ylength){
    output* out = malloc(sizeof(output));
    double *values = malloc(xlength * ylength * sizeof(double));
    for (int i = 0; i < xlength; i++) {
        for (int j = 0; j < ylength; j++) {
            values[i * ylength + j] = roundn(func(x[i], y[j]), 5);
        }
    }
    double trapezoidal = trap(values, xlength, ylength);
    out->values = values;
    out->integral = (x[1]-x[0])*(y[1]-y[0])*trapezoidal/4;
    return out;
}

EXPORT output* simpsons2d(double* x, double* y, double (*func)(double, double), int xlength, int ylength) {
    output* out = malloc(sizeof(output));
    double *values = malloc(xlength*ylength*sizeof(double));
    for(int i = 0; i < xlength ; i++){
        for (int j = 0; j < ylength; j++) {
            values[i * ylength + j] = roundn(func(x[i], y[j]), 5);
        }
    }
    
    double simpsons =  simp(values, xlength, ylength);
    out->values = values;
    out->integral = (x[1]-x[0])*(y[1]-y[0])*simpsons/9;
    return out;
}

EXPORT output* simpsons382d(double* x, double* y, double (*func)(double, double), int xlength, int ylength) {
    output* out = malloc(sizeof(output));
    double *values = malloc(xlength * ylength * sizeof(double));
    for (int i = 0; i < xlength; i++) {
        for (int j = 0; j < ylength; j++) {
            values[i * ylength + j] = roundn(func(x[i], y[j]), 5);
        }
    }
    double simpsons =  simp(values, xlength, ylength);
    out->values = values;
    out->integral = simpsons;
    return out;
}

//=======================================================
double trap(double* values, int xlength, int ylength){
    double* matrix = malloc(xlength * ylength * sizeof(double));
    for(int i = 0; i < xlength; i++){
        for(int j = 0; j < ylength; j++){
            if(i == 0 || j == 0 || i == xlength-1 || j == ylength-1)
                matrix[i * ylength + j] = 2;
            else
                matrix[i * ylength + j] = 4;
        }
    }
    matrix[0] = 1;
    matrix[xlength-1] = 1;
    matrix[(xlength)*(ylength - 1)] = 1;
    matrix[(xlength)*(ylength) - 1] = 1;
    double temp = multiply(values, matrix, xlength);
    free(matrix);
    return temp;
}

double simp(double* values, int xlength, int ylength){
    double matrix[9] = {1,4,1,4,16,4,1,4,1};
    double sum = 0;
    for(int i = 1; i < xlength; i+=2){
        for (int j=1; j < ylength; j+=2){
            sum += multiply(values+(i-1)*ylength+(j-1), matrix, 3);
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

double roundn(double num, int n) {
    // Multiply by 10^n to shift the decimal
    double shifted_num = num * pow(10, n);
    // Round to the nearest integer
    double rounded_shifted_num = round(shifted_num);
    // Divide by 10^n to shift the decimal back
    return rounded_shifted_num / pow(10, n);
}


// double function(double x, double y){
//     return 1/(x*x + y*y);
// }

// int main(){
//     double x[3] = {1,1.5,2};
//     double y[3] = {1,1.5,2};
//     output *k = simpsons2d(x, y, function, 3, 3);
//     printf("Simpsons 1D Integration Result: %f\n", k->integral);
//     for(int i = 0; i < 9; i++){
//         printf("%f ", k->values[i]);
//     }
//     mfree(k);
// }