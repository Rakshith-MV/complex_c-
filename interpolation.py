from sympy import Function, pi, pprint, var, prod, diff, simplify, sqrt
import numpy as np


def lagrange(xn, yn):
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
    L, fu, li = lagrange(xn, yn)    # L = lagrangian polynomial, fu = function for evaluation, li = lagrangian terms
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
    main_diagonal = np.array([1]+[(h[i] + h[i+1])/3 for i in range(n-2)]+[1])
    super_diagonal = np.array([0] + [h[i+1]/6 for i in range(n-2)])
    sub_diagonal = np.array([h[i]/6 for i in range(n-2)]+[0])
    equations = (
    np.diag(sub_diagonal, -1) +
    np.diag(main_diagonal, 0) +
    np.diag(super_diagonal, 1)
    )
    coeffs = np.hstack(([0], np.array([(yn[i+1]-yn[i])/h[i] -  (yn[i] - yn[i-1])/h[i-1] for i in range(1, n-1)]),[0]))
    print(equations)
    print(coeffs, np.shape(coeffs))
    M = np.linalg.solve(equations, coeffs.reshape(1,n))

    # functions = [
    #     1/h[i-1]*((xn[i] - x)**3*M[i-1] +(x - xn[i-1])**3*M[i]/6 + (yn[i-1] - h[i-1]**2*M[i-1]/6)*(xn[i] - x) + (yn[i] - h[i-1]**2*M[i]/6)*(x-xn[i-1])) for i in range(1, n-1)
    # ]
    # return [f.simplify() for f in functions], [lambda v: i.subs(x,v) for i in functions], [lambda v: diff(i,x).subs(x, v) for i in functions]

def test_lagrange():
    
    ... 


if __name__ == "__main__":
    xn = [0, pi/4, pi/2, 3*pi/4, pi]
    yn = [0, 1/np.sqrt(2), 1, 1/np.sqrt(2), 0]
    cubic(xn,yn)
    x = var('x')
    # print(c[0](1))