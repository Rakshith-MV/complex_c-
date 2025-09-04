from scipy.odr import polynomial
from sympy import Function, pprint, var, prod, diff, simplify, sqrt
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

def cubic(xn:list,
          yn:list
          ):
    return "Not Yet implemented"


def newton(xn: list,
              yn: list):
    ...





if __name__ == "__main__":
    x= [0, pi/4 , pi/2 , 3*pi/4, pi]
    y = [0, 1/sqrt(2), 1, 1/sqrt(2),0]