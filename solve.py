from solvers import read, solve_instance
import numpy as np

for i in range(1, 493):
    filename = 'phase1-processed/%d.in' % i
    A, C = read(filename)
    n = A.shape[0]
    d = np.sum(A)/(n*n - n)
    if n < 400 or d <= 0.05:
        solve_instance(i, 5, 0.05)
