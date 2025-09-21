import ctypes 
import numpy as np
from interpolation import hermitian
from matplotlib import pyplot as plt
from nintegration import gaussian

lib = ctypes.CDLL('./src/node.so')

lib.RungeKutta.argtypes = [ctypes.CFUNCTYPE(ctypes.c_double, ctypes.c_double, ctypes.c_double), ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double]
lib.RungeKutta.restype = ctypes.POINTER(ctypes.c_double)

lib.euler_first.argtypes = [ctypes.CFUNCTYPE(ctypes.c_double, ctypes.c_double, ctypes.c_double), ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double]
lib.euler_first.restype = ctypes.POINTER(ctypes.c_double)

lib.RungeKutta2.argtypes = [ctypes.CFUNCTYPE(ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double), ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double]
lib.RungeKutta2.restype = ctypes.POINTER(ctypes.c_double)


SFUNC_TYPE = ctypes.CFUNCTYPE(ctypes.c_double, ctypes.c_double, ctypes.c_double)
DFUNC_TYPE = ctypes.CFUNCTYPE(ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double)


#Why is there an error in addition
#The error in addition is likely due to the way the y values are being calculated and stored.
#In the actual_solver function, the y values are being calculated using solve_ivp, which returns a different structure than expected.
#We need to extract the y values correctly from the result of solve_ivp.


#functions start here.......
#-------------------------------------------------------------------------------

def runge_kutta(func, x0, xn, y0, h):
    c_func = SFUNC_TYPE(func)
    result_ptr = lib.RungeKutta(c_func, x0, xn, y0, h)
    length = int((xn - x0) / h) + 1
    result = [result_ptr[i] for i in range(length)]
    # Free the allocated memory in C
    lib.mfree(result_ptr)
    return [x0+i*h for i in range(length)] , result


def runge_kutta2(g, x0, xn , y0, dy0, h):
    """
    Put in just the g(x,y,z), as f(x,y,z) is just z
    """
    g_func = DFUNC_TYPE(g)

    result_ptr = lib.RungeKutta2(g_func, x0, xn, y0, dy0, h)
    length = int((xn - x0) / h) + 1
    result = [result_ptr[i] for i in range(2*length)]
    lib.mfree(result_ptr)
    return [x0+i*h for i in range(length)], result[:length], result[length:] 

def euler_first(func, x0, xn, y0, h):
    c_func = SFUNC_TYPE(func)
    result_ptr = lib.euler_first(c_func, x0, xn, y0, h)
    length = int((xn - x0) / h) + 1
    result = [result_ptr[i] for i in range(length)]
    # Free the allocated memory in C
    lib.mfree(result_ptr)
    return result

def adams_bashforth(func, x0, xn, y0, h):
    x_val, values = runge_kutta(func, x0, xn, y0, h)
    f = [func(i,j) for i,j in zip(x_val, values)]
    for i in range(4, len(values)):
        values[i] = values[i-1] + h/24 *(55*f[i] - 59*f[i-1] + 37*f[i-2] - 9*f[i-3])  #predictor
        values[i] = values[i-1] + h/24 * (9*f[i] + 19*f[i-1] - 5*f[i-2] + f[i-3])  #corrector
    return x_val, values

def milne(func, x0, xn, y0, h):
    x_val, values = runge_kutta(func, x0, xn, y0, h)
    f = [func(i,j) for i,j in zip(x_val, values)]
    for i in range(4, len(values)):
        values[i] = values[i-4] + 4*h/3 * (2*f[i-3] - f[i-2] + 2*f[i-1])  #predictor
        values[i] = values[i-2] + h/3 * (f[i-2] + 4*f[i-1] + f[i])  #corrector
    return x_val, values

#testing
if __name__ == "__main__":
    def func(x, y, z):
        return x*z - y
    def f(x,y,z):
        return 6*y - z
    x, y, z = runge_kutta2(f, 0, 0.2, 3, 1, 0.1)