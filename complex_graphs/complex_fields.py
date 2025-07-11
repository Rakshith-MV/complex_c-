from numpy import linspace, array, inf, sqrt, arctan2, pi, cos, sin


class element:
    def __init__(self, real, imag, rep=0):
        if rep == 0:
            self.real = float(real)
            self.imag = float(imag)
            self.abs = float(sqrt(real**2 + imag**2))
            self.t = arctan2(imag, real) if real != 0 else pi/2
        else:
            self.abs = real
            self.t = imag
            self.real = real*cos(imag)
            self.imag = real*sin(imag)
            
    def __add__(self, 
                other:element)->element: # type: ignore
        return element(self.real + other.real, self.imag + other.imag)

    #slightly better
    def __mul__(self, other:element)->element:  # type: ignore
        angle = self.t + other.t
        return element(self.abs * other.abs, -(2*pi - angle) if angle > pi else angle, 1)
        
    def __matmul__(self, other:element)->element:  # type: ignore
        # (a + bi)(c + di) = (ac - bd) + (ad + bc)i
        real_part = self.real * other.real - self.imag * other.imag
        imag_part = self.real * other.imag + self.imag * other.real
        return element(real_part, imag_part)    

    def __str__(self):
        return f"{self.real} + {self.imag}i"

    def __add__(self, 
                other:element)->element:  # type: ignore
        return element(self.real + other.real, self.imag +other.imag)

    def __sub__(self,
                other:element)->element: # type: ignore
        return element(self.real -other.real, self.imag-other.imag)

    def conjugate(self):
        return element(self.abs, -self.t,1)

    def __pow__(self,n
                )->element:  # type: ignore
        angle = n*self.t
        return element(self.abs ** n, -(2*pi-angle) if angle > pi else angle, 1) 
    
    def __truediv__(self, 
                    other:element)->element:  # type: ignore
        if other.abs == 0:
            return inf
        return self * other.inverse()

    def inverse(self):
        # Multiplicative inverse: 1/(a + bi) = (a - bi)/(a^2 + b^2)
        try:
            return element(1/self.abs, -self.t,1)
        except:
            return element(0, 0, 1)  # Handle division by zero gracefully


class complexfield(element):
    def __init__(self,mx=-5,Mx=5,my=-5,My=5, field=0):
        if field == 0:   #we could vectorize everythng here
            self.grid = array([[(i,j) for i in linspace(mx,Mx,500)] for j in linspace(my, My, 500)])
            self.elements = array([[element(*i) for i in j] for j in self.grid])
        else:
            self.elements = field

    def __pow__(self,n):
        return complexfield(field=array([[i**n for i in j] for j in self.elements]))
    
    def abs(self):
        return array([[i.abs for i in j] for j in self.elements])

    def real(self):
        return array([[i.real for i in j] for j in self.elements])

    def imag(self):
        return array([[i.imag for i in j] for j in self.elements])

    def angle(self):
        return array([[i.t for i in j] for j in self.elements])


    # Operations with complex fields
    # These methods allow operations with other complex fields

    def __add__(self,
            c:complexfield):  # type: ignore
        return complexfield(self.elements+c.elements,field=1)
    
    def __sub__(self,
              c:complexfield):  # type: ignore
        return complexfield(self.elements-c.elements, field=1)

    def __mul__(self,
                c:complexfield):  # type: ignore
        return complexfield(self.elements*c.elements, field=1)

    def __div__(self,
                c:complexfield): # type: ignore
        return complexfield(self.elements/c.elements, field=1)

    def function(self, f):
        return f(self)        


    # Operations with complex numbers
    # These methods allow operations with single complex numbers
    def __add__(self, 
                c:element):
        return complexfield(self.elements+c, field=1)

    def __sub__(self,
              c:element):
        return complexfield(self.elements-c, field=1)

    def __mul__(self,
                c:element):
        return complexfield(self.elements*c, field=1)

    def __div__(self,
                c:element):
        return complexfield(self.elements*c.inverse(), field=1)

    def function(self, f):
        return f(self)        
    



def test():
    C = complexfield(-5,5,-5,5)
    C2 = C.function(lambda x: (x+1)/(x+2))
    print(C2.real())
    print(C2.imag())
    print(C2.abs())
    print(C2.angle())
    print(C2**2)
    print(C2+C2)
    print(C2-C2)
    print(C2*C2)
    print(C2/C2)

if __name__ == "__main__":
    test()