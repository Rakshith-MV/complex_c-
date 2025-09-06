import ctypes
import math

class Output(ctypes.Structure):
    _fields_ = [
        ("values", ctypes.POINTER(ctypes.c_double)),
        ("integral", ctypes.c_double)
    ]
    def convert(self,xlength,ylength: int = 1):
        try:
            return {'data':[self.values[i] for i in range(xlength*ylength)],
                'integral_value': self.integral}
        except:
            return {'data':None,
                'integral_value': self.integral}
FUNC_TYPE = ctypes.CFUNCTYPE(ctypes.c_double, ctypes.c_double, ctypes.c_double)
SFUNC_TYPE = ctypes.CFUNCTYPE(ctypes.c_double, ctypes.c_double)
lib = ctypes.CDLL('./src/integration.so')


lib.trapezoidal2d.argtypes = [
    ctypes.POINTER(ctypes.c_double),  # double* x
    ctypes.POINTER(ctypes.c_double),  # double* y  
    FUNC_TYPE,                        # double (*func)(double, double)
    ctypes.c_int,
    ctypes.c_int                       # double k
]
lib.trapezoidal2d.restype = ctypes.POINTER(Output)

lib.simpsons2d.argtypes = [
    ctypes.POINTER(ctypes.c_double),  # double* x
    ctypes.POINTER(ctypes.c_double),  # double* y
    FUNC_TYPE,                        # double (*func)(double, double)
    ctypes.c_int,
    ctypes.c_int                       # double k
]
lib.simpsons2d.restype = ctypes.POINTER(Output)


lib.simpsons382d.argtypes = [ctypes.POINTER(ctypes.c_double),  # double* x
    ctypes.POINTER(ctypes.c_double),  # double* y
    FUNC_TYPE,                        # double (*func)(double, double)
    ctypes.c_int,
    ctypes.c_int                       # double k
]
lib.simpsons382d.restype = ctypes.POINTER(Output)



#=====================================================
lib.trapezoidal1d.argtypes = [
    ctypes.POINTER(ctypes.c_double),  # double* x
    SFUNC_TYPE,                        # double (*func)(double)
    ctypes.c_int
]
lib.trapezoidal1d.restype = ctypes.POINTER(Output)

lib.simpsons1d.argtypes = [
    ctypes.POINTER(ctypes.c_double),  # double* x
    SFUNC_TYPE,                        # double (*func)(double)
    ctypes.c_int
]
lib.simpsons1d.restype = ctypes.POINTER(Output)

lib.simpsons381d.argtypes = [
    ctypes.POINTER(ctypes.c_double),  # double* x
    SFUNC_TYPE,                        # double (*func)(double)
    ctypes.c_int
]
lib.simpsons381d.restype = ctypes.POINTER(Output)

lib.gaussian.argtypes = [
    SFUNC_TYPE, 
    ctypes.c_double, 
    ctypes.c_double]
lib.gaussian.restype = ctypes.POINTER(Output)

lib.mfree.argtypes = [ctypes.POINTER(Output)]
lib.mfree.restype = None


def trapezoidal1d_integrate(x0, xn, h, f):
    length = int((xn-x0)/h)+1
    x_array = (ctypes.c_double * (length))(*[x0+i*h for i in range(length)])
    f_func = SFUNC_TYPE(f)
    result = lib.trapezoidal1d(x_array, f_func, length).contents
    result_trapezoidal = result.convert(length)
    lib.mfree(result)
    return result_trapezoidal

def simpsons1d_integrate(x0, xn, h, f):
    length = int((xn-x0)/h)+1
    x_array = (ctypes.c_double * (length))(*[x0+i*h for i in range(length)])
    f_func = SFUNC_TYPE(f)
    result = lib.simpsons1d(x_array, f_func, length).contents
    result_simpsons = result.convert(length)
    lib.mfree(result)
    return result_simpsons

def simpsons381d_integrate(x0, xn, h, f):
    length = int((xn-x0)/h)+1
    x_array = (ctypes.c_double * (length))(*[x0+i*h for i in range(length)])
    f_func = SFUNC_TYPE(f)
    result = lib.simpsons381d(x_array, f_func, length).contents
    result_simpson38 = result.convert(length)
    lib.mfree(result)
    return result_simpson38

def gaussian(f, a, b):
    f_func = SFUNC_TYPE(f)
    result = lib.gaussian(f_func, a, b).contents
    result_gauss = result.convert(1)
    lib.mfree(result)
    return {'two': result_gauss['integral_value'],
            'three': result_gauss['data'][0]}

def sintegrate(x0,xn,h,f):
    result_trapezoidal = trapezoidal2d_integrate(x0, xn,  h, f)
    result_simpsons = simpsons2d_integrate(x0, xn, h, f)
    result_simpson38 = simpsons382d_integrate(x0, xn, h, f)
    result_gaussian = gaussian(f, x0, xn)
    return {"simpsons_1/3rd": result_simpsons,
            "trapezoidal": result_trapezoidal,
            "simpsons_3/8th": result_simpson38,
            "gaussian": result_gaussian}
            


def trapezoidal2d_integrate(x0, xn, y0, yn, h, k, f):
    xlength = int((xn-x0)/h)+1
    ylength = int((yn-y0)/k)+1
    x_array = (ctypes.c_double * (xlength))(*[x0+i*h for i in range(xlength)])
    y_array = (ctypes.c_double * (ylength))(*[y0+i*k for i in range(ylength)])
    f_func = FUNC_TYPE(f)
    result = lib.trapezoidal2d(x_array, y_array, f_func, xlength, ylength).contents    
    result_trapezoidal = result.convert(xlength, ylength)
    lib.mfree(result)
    return result_trapezoidal

def simpsons2d_integrate(x0, xn, y0, yn, h, k, f):
    xlength = int((xn-x0)/h)+1
    ylength = int((yn-y0)/k)+1
    x_array = (ctypes.c_double * (xlength))(*[x0+i*h for i in range(xlength)])
    y_array = (ctypes.c_double * (ylength))(*[y0+i*k for i in range(ylength)])
    f_func = FUNC_TYPE(f)
    result = lib.simpsons2d(x_array, y_array, f_func, xlength, ylength).contents
    result_simpsons = result.convert(xlength, ylength)
    lib.mfree(result)
    return result_simpsons

def simpsons382d_integrate(x0, xn, y0, yn, h, k, f):
    xlength = int((xn-x0)/h)+1
    ylength = int((yn-y0)/k)+1
    x_array = (ctypes.c_double * (xlength))(*[x0+i*h for i in range(xlength)])
    y_array = (ctypes.c_double * (ylength))(*[y0+i*k for i in range(ylength)])
    f_func = FUNC_TYPE(f)
    result = lib.simpsons382d(x_array, y_array, f_func, xlength, ylength).contents
    result_simpson38 = result.convert(xlength, ylength)
    lib.mfree(result)
    return result_simpson38

# You can modify the existing integrate function to use these new functions:
def dintegrate(x0, xn, y0, yn, f, h, k):
    result_trapezoidal = trapezoidal2d_integrate(x0, xn, y0, yn, h, k, f)
    result_simpsons = simpsons2d_integrate(x0, xn, y0, yn, h, k, f)
    result_simpson38 = simpsons382d_integrate(x0, xn, y0, yn, h, k, f)
    
    return {"simpsons_1/3rd": result_simpsons,
            "trapezoidal": result_trapezoidal,
            "simpsons_3/8th": result_simpson38}

def romberg_integration(f, a, b, tol=1e-6, max_iter=10):
    # Romberg integration implementation
    return result

if __name__ == "__main__":
    print("Running tests on numerical integration.......")

    f = lambda x,y: 1/(x**2 + y**2)
    result = simpsons2d_integrate(1,2,1,2,0.5,0.5,f)
    assert abs(float(result['integral_value']) - 0.231169) < 1e-3, f"Expected 0.231169, got {result['integral_value']}"
    
    f = lambda x,y: 1/(1+x+y)
    result = simpsons2d_integrate(0,1,0,1,0.5,0.5,f)
    assert abs(float(result['integral_value']) - 0.524074) < 1e-3, f"Expected 0.524074, got {result['integral_value']}"

    f = lambda x,y: x*math.exp(y)
    result = trapezoidal2d_integrate(0,1,0,1,0.5,0.5,f)
    assert abs(float(result['integral_value']) - 0.8770) < 1e-3, f"Expected 0.8770, got {result['integral_value']}"

    f = lambda x,y: 1/math.sqrt(x**2+y**2)
    result = trapezoidal2d_integrate(1,5, 1, 5, 2,2,f)
    assert abs(float(result['integral_value']) - 4.1343) < 1e-3, f"Expected 4.1343, got {result['integral_value']}"
    


    f = lambda x: 1/x
    result = trapezoidal1d_integrate(1, 2, 0.2, f)
    assert abs(float(result['integral_value']) - 0.695635) < 1e-4, f"Expected 0.695635, got {result['integral_value']}"
    
    result = simpsons1d_integrate(1, 2, 0.1, f)
    assert abs(float(result['integral_value']) - 0.693150) < 1e-4, f"Expected 0.693150, got {result['integral_value']}"

    f = lambda x: math.exp(x**2)
    result = simpsons1d_integrate(0, 1, 0.1, f)
    assert abs(float(result['integral_value']) - 1.462681) < 1e-4, f"Expected 1.462681, got {result['integral_value']}"

    f = lambda x: math.exp(-x/2)
    result = gaussian(f, -2, 2)
    assert abs(float(result['two']) - 4.6853) < 1e-4, f"Expected 4.6853, got {result['two']}"

    f = lambda x: math.exp(x)*math.cos(x) - 2*x
    result = gaussian(f, 0, 1)
    assert abs(float(result['three']) - 0.37802) < 1e-4, f"Expected 0.37802, got {result['three']}"
    
    print("Started")
    f = lambda x: math.sin(x)/(2+3*math.sin(x))
    result = simpsons381d_integrate(0,1,1/6,f)
    for i in result['data']:
        print(i)
    assert abs(float(result['integral_value']) - 0.1250) < 1e-4, f"Expected 0.1250, got {result['integral_value']}"

    print("Integration tests passed...")