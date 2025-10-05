// #include<stdio.h>
#include<math.h>
#include<stdlib.h>


#ifndef ANDROID
    #define EXPORT __attribute__((visibility("default")))
#endif

double trap(double*, int, int);
double multiply(double*, double*, int);
double simp(double*, int, int);
// double function( double);
double roundn(double , int );


typedef struct {
    double* values;
    double* graph;
    double integral;
} output;


EXPORT void mfree(output* out){
    if(out){
        free(out->values);
        free(out->graph);
        free(out);
    }
}

EXPORT output* trapezoidal1d(double* x, double (*func)(double), int length){
    output* out = malloc(sizeof(output));
    double *values = malloc(length * sizeof(double));
    double *graph = malloc(length * sizeof(double));
    double sum = 0.0;
    for (int i = 0; i < length; i++) {
        values[i] = func(x[i]);
        sum = sum + 2*values[i];   
    }
    for(int i = 1; i < length; i++){
        graph[i] = (values[i] + values[i-1])/2;
    }
    graph[0] = length - 1;
    sum = sum - (values[0] + values[length-1]);
    sum = sum * (x[1] - x[0]) / 2;
    out->values = values;
    out->graph = graph;
    out->integral = sum;
    return out;
}

EXPORT output* simpsons1d(double* x, double (*func)(double), int length){
    output* out = malloc(sizeof(output));
    double *values = malloc(length * sizeof(double));
    double *graph = malloc(length * sizeof(double));
    double sum = 0.0;
    int i = 1;
    while(i < length-1){
        if(i % 2 == 0){
            values[i] = func(x[i]);
            sum += 2*values[i];
        }
        else{
            values[i] = func(x[i]);
            sum += 4*values[i];
        }
        i++;
    }

    values[0] = func(x[0]);
    values[length-1] = func(x[length-1]);
    sum += values[0] + values[length-1];
    sum *= (x[1] - x[0]) / 3;
    i = 1;
    for(int j = 0; j < length-2; j+=2, i++){
        graph[i] = (values[j] + 4*values[j+1] + values[j+2])/6;
    }
    graph[0] = i-1;
    out->graph = graph;
    out->values = values;
    out->integral =  sum;
    return out;
}

EXPORT output* simpsons381d(double* x, double (*func)(double), int length){
    output *out = malloc(sizeof(output));
    double *values = malloc(length* sizeof(double));
    double *graph = malloc(length * sizeof(double));
    int j = 0;
    double sum = 0;
    for(int i = 0; i<length; i++){
        values[i] = roundn(func(x[i]),5);
    }
    while(j < length-1){             // why length -1 ???
        sum  += values[j] + 3*values[j+1] + 3*values[j+2] + values[j+3];
        j = j+3;
    }
    j = 1;
    for(int i = 0; i < length-3; i+=3, j++){
        graph[j] = (values[i] + 3*values[i+1] + 3*values[i+2] + values[i+3])/8;
    }
    graph[0] = j-1;
    out->values = values;
    out->graph = graph;
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

// double function(double x){
//     return exp(x)/x;
// }

// int main(){
//     double x[30];
//     for(int i = 0; i <= 29; i++){
//         x[i] = 1 + i/29.0;
//     }
//     output *k = trapezoidal1d(x, function, 30);
//     printf("Simpsons 1D Integration Result: %f\n", k->integral);
//     for(int i = 0; i < 30; i++){
//         printf("f(%f) = %f, %f\n", x[i], k->values[i]);
//         // printf("f(%f) = %f\n", x[i], k->graph[i]);
//     }
//     for(int i = 0; i < k->graph[0]; i++){
//         printf("Graph %d: %f\n", i, k->graph[i]);
//     }
//     mfree(k);
// }