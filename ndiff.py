import ctypes
import math

class Output(ctypes.Structure):
    _fields_ = [
        ("values", ctypes.POINTER(ctypes.c_double)),
        ("integral", ctypes.c_double)
    ]
    def convert(self,length):
        return {'data':[self.values[i] for i in range(length*length)],
                'integral_value': self.integral}
    
FUNC_TYPE = ctypes.CFUNCTYPE(ctypes.c_double, ctypes.c_double, ctypes.c_double)


lib = ctypes.CDLL('./src/diff.so')