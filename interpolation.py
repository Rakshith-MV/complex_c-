from scipy.odr import polynomial
from sympy import Function, var, prod, diff, simplify, sqrt
import numpy as np

from numpy import pi as pi

def lagrange(xn:list,
             yn:list):
    x = var('x')
    n = len(xn)
    p = Function('p')
    lagrangian_terms = [prod((x - xn[j]) / (xn[i] - xn[j]) for j in range(n) if j != i) for i in range(n)]
    p = sum([yn[i]*lagrangian_terms[i] for i in range(n)])
    return p.simplify(), lambda a: p.subs(x, a), lagrangian_terms

def hermitian(xn: list, 
              yn: list,
              y1: list):
    x = var('x')
    L, fu, li = lagrange(xn, yn)
    n = len(xn)
    h = Function('h')
    hermitian_terms = [li[i]**2 * yn[i] * (1-2*(x-xn[i])*diff(li[i],x).subs(x,xn[i])) + (x - xn[i]) *li[i]**2 * y1[i] for i in range(n)]
    return sum(hermitian_terms).simplify(), lambda a: sum(hermitian_terms).subs(x, a), lambda a: sum(hermitian_terms).diff(x).subs(x, a)

def TA(a,d,b,r,x):
    n=len(a)
    a[0]=a[0]/d[0]
    r[0]=r[0]/d[0]
    for i in range (1,n):
        den=(d[i]-(b[i]*a[i-1]))
        a[i]=a[i]/den
        r[i]=(r[i]-(b[i]*r[i-1]))/den
    for i in range(1,n+1):
        x[-i]=r[-i]-(a[-i]*x[-(i-1)])
    return x

def cubic(xn:list,
          yn:list
          ):
    """
    n points, n-1 equations
    """
    n = len(xn)
    h = xn[1]-xn[0]
    v = [0]+ [6*(yn[i+1]-2*yn[i]+yn[i-1])/h**2 for i in range(1,n-1)] + [0]
    a = [0] + (n-1)*[1]
    b = (n-1)*[1]+[0]
    d = n*[4]
    M = [0] + TA(a, d, b, v, n*[0]) + [0]
    x = var('x')
    polynomials = []
    for i in range(1,n):
        H = Function('x')
        H = (1/h*((xn[i]-x)**3 * M[i-1] /6  + (x-xn[i-1])**2 *M[i]/6 + (yn[i-1] - h**2 *M[i]/6 )*(xn[i] -x)  + (yn[i] - h**2 *M[i] /6)*(x-xn[i-1])))
        polynomials.append(H)
    def val(p):
        i = 0
        while(p < xn[i]): 
            i+=1
        return (polynomials[i]).subs(x,p)
    return polynomials, val, M


if __name__ == "__main__":
    x= [0, pi/4 , pi/2 , 3*pi/4, pi]
    y = [0, 1/sqrt(2), 1, 1/sqrt(2),0]
    p, f = cubic(x,y)
