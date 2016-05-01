from solvers import read, solve_instance, preprocess
import numpy as np

def solve_constantino(l, r):
    for i in range(l, r):
        filename = 'phase1-processed/%d.in' % i
        A, C = read(filename)
        subproblems = preprocess(A, C, 5)
        ns = [A_i.shape[0] for A_i, _, _ in subproblems]
        n = max(ns)
        ds = [np.sum(A_i)/(A_i.shape[0]**2 - A_i.shape[0]) for A_i, _, _ in subproblems]
        d = max(ds)
        if n <= 250 or d <= 0.05:
            solve_instance(i, 5, 0.01)

def solve_two_cycle(l, r):
    for i in range(l, r):
        solve_instance(i, 5, 0.01)

solve_constantino(1, 50)
