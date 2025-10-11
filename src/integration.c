#include<stdio.h>
#include<math.h>
#include<stdlib.h>


#ifndef ANDROID
    #define EXPORT __attribute__((visibility("default")))
#endif

double trap(double*, int, int);
double multiply(double*, double*, int);
double simp(double*, double*,int, int);
double simp38(double*, double*, int, int);
double function( double, double);
double roundn(double , int );


typedef struct {
    double* values;
    double* graph;
    double integral;
} output;


EXPORT void mfree(output* out){
    if(out != NULL){
        if (out->graph != NULL)
            free(out->graph);
        if (out->values != NULL)
            free(out->values);
        free(out);
    }
}
EXPORT void gfree(output* out){
    if(out != NULL){
        if (out->values != NULL)
            free(out->values);
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
    graph[0] = length;
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
    graph[0] = i;
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
    for(int i = 0; i <= length-3; i+=3, j++){   // check here is i <= or i < 
        graph[j] = (values[i] + 3*values[i+1] + 3*values[i+2] + values[i+3])/8;
    }
    graph[0] = j;  // don't why this worked, fuck
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
    out->graph = malloc(sizeof(double));
    out->graph[0] = 0;
    out->values[0] = three_points;
    return out;
}      

// ============================================================================================
EXPORT output* trapezoidal2d(const double* x, const double* y, double (*func)(double, double), int xlength, int ylength){
    /*
    Trapezoidal rule for 2D integration
    it creates values and graph array
    computed on trap function
    */
    output* out = malloc(sizeof(output));
    out->values = malloc(xlength * ylength * sizeof(double));
    out->graph = malloc((xlength-1) *(ylength -1)*sizeof(double));
    for (int i = 0; i < xlength; i++) {
        for (int j = 0; j < ylength; j++) {
            out->values[i * ylength + j] = roundn(func(x[i], y[j]), 5);
        }
    }
    for(int i = 0; i < xlength-1; i++){
        for(int j = 0; j < ylength-1; j++){
            out->graph[i*(ylength-1) + j] = (out->values[i*(ylength-1)+j] + out->values[i*(ylength-1)+j+1])/2;
        }
    }
    out->integral = (x[1]-x[0])*(y[1]-y[0])*trap(out->values, xlength, ylength)/4;
    return out;
}

EXPORT output* simpsons2d(double* x, double* y, double (*func)(double, double), int xlength, int ylength) {
    output* out = malloc(sizeof(output));
    out->values = malloc(xlength*ylength*sizeof(double));
    out->graph = malloc((int)xlength/2 * (int)ylength/2 * sizeof(double));
    for(int i = 0; i < xlength ; i++){
        for (int j = 0; j < ylength; j++) {
            out->values[i * ylength + j] = roundn(func(x[i], y[j]), 5);
        }
    }
    out->integral = (x[1]-x[0])*(y[1]-y[0])*simp(out->values, out->graph, xlength, ylength)/9;
    return out;
}

EXPORT output* simpsons382d(double* x, double* y, double (*func)(double, double), int xlength, int ylength) {
    output* out = malloc(sizeof(output));
    out->values = malloc(xlength * ylength * sizeof(double));
    out->graph = malloc((int)(xlength/3)*(int)(ylength/3)*sizeof(double));
    for (int i = 0; i < xlength; i++) {
        for (int j = 0; j < ylength; j++) {
            out->values[i * ylength + j] = roundn(func(x[i], y[j]), 5);
        }
    }
    double simpsons =  simp38(out->values, out->graph, xlength, ylength);
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

double simp(double* values, double* graph, int xlength, int ylength){
    double matrix[9] = {1,4,1,4,16,4,1,4,1};
    double sum = 0;
    double temp = 0;
    int index = 1;
    for(int i = 1; i < xlength; i+=2){
        for (int j=1; j < ylength; j+=2){
            temp = multiply(values+(i-1)*ylength+(j-1), matrix, 3);
            sum += temp;
            graph[index] = temp/16;
            index++;
        }
    }
    graph[0] = index-1;
    return sum;
}

double simp38(double* values, double* graph, int xlength, int ylength){
    double matrix[16] = {1,3,3,1,3,9,9,3,3,9,9,3,1,3,3,1};
    double sum = 0;
    double temp = 0;
    int index = 1;
    for(int i = 1; i < xlength; i+=3){
        for (int j=1; j < ylength; j+=3){
            temp = multiply(values+(i-1)*ylength+(j-1), matrix, 4);
            sum += temp;
            graph[index] = temp/64;
            index++;
        }
    }
    graph[0]= index-1;
    return 3*sum/8;
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

double function(double x, double y){
    return 1/sqrt(x*x + y*y);
}

int main(){
    double x[] = {1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0};
    double y[] = {1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0}; 

    output *k = simpsons382d(x, y, function, 7, 7);
    printf("Integral : %f\n", k->integral);
    for(int i = 0; i < 7*7; i++){
        if (i % 5 == 0){
            printf("\n");
        }
        printf("%f\n ", k->values[i]);
    }
    printf("Graphs \n");
    for(int i = 0; i < 4; i++){
        if (i % 2 == 0){
            printf("\n");
        }
        printf("%f\n ", k->graph[i]);
    }
    printf("\n");
    mfree(k);
}