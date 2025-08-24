from scipy.odr import polynomial
from sympy import Function, pprint, var, prod, diff, simplify, sqrt
import numpy as np
import numpy as pi

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
    x = var('x')
    n = len(xn)
    h = [xn[i+1] - xn[i] for i in range(n-1)]
    
    #Define the diagonal elements properly
    main_diagonal = np.array([1/3*(h[i]+h[i+1]) for i in range(n)], dtype=np.float32)
    super_diagonal = np.array([0] + [1 for i in range(n-2)], dtype=np.float32)
    sub_diagonal = np.array([1 for i in range(n-2)]+[0], dtype=np.float32)
    equations = (
    np.diag(sub_diagonal, -1) +
    np.diag(main_diagonal, 0) +
    np.diag(super_diagonal, 1)
    )
    print("Equations:", equations)
    coeffs = np.hstack(([0]+[(yn[i+1]-yn[i])/h[i] -  (yn[i] - yn[i-1])/h[i-1] for i in range(1, n-1)]+[0]))
    print("Coefficients:", coeffs)
    M = np.linalg.solve(equations.astype(np.float32), coeffs.astype(np.float32))
    polynomials = [
        1/h[i] *((xn[i+1] - x)**3*M[i]/6 + (x - xn[i])**3*M[i+1]/6 + (yn[i] - h[i]**2*M[i]/6)*(xn[i+1]-x) +(yn[i+1] - h[i]**2*M[i+1]/6)*(x - xn[i])) for i in range(n-1)
    ]
    polynomials = [i.simplify().expand().simplify().simplify() for i in polynomials]
    dpoly = [i.diff().simplify().expand().simplify().simplify() for i in polynomials]
    def value(v, I=xn):
        i = 0
        try:
            while not ((v >= I[i]) and (v < I[i+1])):
                i+=1
        except IndexError:
            return 0
        return polynomials[i].subs(x,v)
    def dvalue(v, I=xn):
        i = 0
        try:
            while not ((v >= I[i]) and (v <= I[i+1])):
                i+=1
        except IndexError:
            return 0
        return dpoly[i].subs(x,v)
    return polynomials, value , dvalue, M 