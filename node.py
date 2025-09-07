import ctypes 
import math
from interpolation import hermitian
from matplotlib import pyplot as plt
import numpy as np

lib = ctypes.CDLL('./src/node.so')

lib.RungeKutta.argtypes = [ctypes.CFUNCTYPE(ctypes.c_double, ctypes.c_double, ctypes.c_double), ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double]
lib.RungeKutta.restype = ctypes.POINTER(ctypes.c_double)

lib.euler_first.argtypes = [ctypes.CFUNCTYPE(ctypes.c_double, ctypes.c_double, ctypes.c_double), ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double]
lib.euler_first.restype = ctypes.POINTER(ctypes.c_double)

SFUNC_TYPE = ctypes.CFUNCTYPE(ctypes.c_double, ctypes.c_double, ctypes.c_double)







#functions start here.......
#-------------------------------------------------------------------------------
def runge_kutta(func, x0, xn, y0, h):
    c_func = SFUNC_TYPE(func)
    result_ptr = lib.RungeKutta(c_func, x0, xn, y0, h)
    length = int((xn - x0) / h) + 1
    result = [result_ptr[i] for i in range(length)]
    # Free the allocated memory in C
    lib.mfree(result_ptr)
    print(result)
    return result

def euler_first(func, x0, xn, y0, h):
    c_func = SFUNC_TYPE(func)
    result_ptr = lib.euler_first(c_func, x0, xn, y0, h)
    length = int((xn - x0) / h) + 1
    result = [result_ptr[i] for i in range(length)]
    # Free the allocated memory in C
    lib.mfree(result_ptr)
    print(result)
    return result








#testing 
if __name__ == "__main__":
    def func(x, y):
        return y - x**2 + 1

    x0 = 0
    xn = 2
    y0 = 0.5
    h = 0.1

    print("Euler's Method Results:")
    y_val = euler_first(func, x0, xn, y0, h)
    x_val = [x0 + i*h for i in range(int((xn - x0)/h) + 1)]
    y1 = [func(i,j) for i,j in zip(x_val, y_val)]
    a, b, c = hermitian(x_val, y_val, y1)
    
    x_val = np.linspace(x0, xn, 500)
    y_val = [b(i) for i in x_val]
    plt.plot(x_val, y_val, label="Euler's Method", color='blue')
    plt.show()

    
    print("\nRunge-Kutta Method Results:")
    y2 = runge_kutta(func, x0, xn, y0, h)