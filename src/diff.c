#include<stdlib.h>
#include<math.h>

#ifndef ANDROID
    #define EXPORT __attribute__((visibility("default")))
#endif

struct output {
    double *values;
    double integral;
};

EXPORT struct output *create_output(int length) {
    struct output *out = malloc(sizeof(struct output));
    out->values = malloc(length * sizeof(double));
    out->integral = 0.0;
    return out;
}

EXPORT void free_output(struct output *out) {
    free(out->values);
    free(out);
}