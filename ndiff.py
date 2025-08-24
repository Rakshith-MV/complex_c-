import ctypes
import math

class Output(ctypes.Structure):
    _fields_ = [
        ("values", ctypes.POINTER(ctypes.c_double)),
        ("integral", ctypes.c_double)
    ]
    def convert(self,length):
        self.data = [self.values[i] for i in range(length*length)]
        self.integral_value = self.integral
FUNC_TYPE = ctypes.CFUNCTYPE(ctypes.c_double, ctypes.c_double, ctypes.c_double)

lib = ctypes.CDLL('./src/diff.so')


lib.trapezoidal.argtypes = [
    ctypes.POINTER(ctypes.c_double),  # double* x
    ctypes.POINTER(ctypes.c_double),  # double* y  
    FUNC_TYPE,                        # double (*func)(double, double)
    ctypes.c_int                   # double k
]
lib.trapezoidal.restype = ctypes.POINTER(Output)

lib.simpsons.argtypes = [
    ctypes.POINTER(ctypes.c_double),  # double* x
    ctypes.POINTER(ctypes.c_double),  # double* y
    FUNC_TYPE,                        # double (*func)(double, double)
    ctypes.c_int
]
lib.simpsons.restype = ctypes.POINTER(Output)

lib.mfree.argtypes = [ctypes.POINTER(Output)]
lib.mfree.restype = None

def integrate(x0,xn,y0,yn, f,h,k):
    length = int((xn-x0)/h)+1
    x_array = (ctypes.c_double * (length))(*[x0+i*h for i in range(length)])
    y_array = (ctypes.c_double * (length))(*[y0+i*k for i in range(length)])
    f_func = FUNC_TYPE(f)


    result_trapezoidal = lib.trapezoidal(x_array, y_array, f_func, length).contents
    
    result_trapezoidal.convert(length)
    result_trapezoidal.integral_value *= (h * k / 4)

    result_simpsons = lib.simpsons(x_array, y_array, f_func, length).contents
    result_simpsons.convert(length)
    result_simpsons.integral_value *= (h * k / 9)



    lib.mfree(result_trapezoidal)
    lib.mfree(result_simpsons)

    return {"simpsons_1/3rd": result_simpsons,
             "trapezoidal": result_trapezoidal,
             "simpsons_3/8th":None}

if __name__ == "__main__":  
    h, k = 0.5, 0.5
    f = lambda x, y: math.exp(x+y)
    integrate(0, 1, 0, 1, f, h, k)