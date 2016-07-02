from solvers import read_instance, check_cycles, preprocess
import numpy as np
from statistics import mean, median, stdev

N = 492
k = 5

def print_instance_stats():
    instances = (read_instance(i) for i in range(1, N + 1))
    ns = []
    ds = []
    for i in range(N):
        A, C = next(instances)
        subproblems = preprocess(A, C, k)
        for j, subproblem in enumerate(subproblems):
            A_j, _, _ = subproblem
            n = A_j.shape[0]
            ns.append(n)
            d = 0.0
            if n > 2:
                d = np.sum(A_j)/float(n*n - n)
            d = float(d)
            ds.append(d)
            print('[%d.%d] : n = %d; d = %0.2f' % (i+1, j+1, n, d))

    print('n avg: %d, med: %0.2f, stdev: %0.2f' % (mean(ns), median(ns), stdev(ns)))
    print('d avg: %0.2f, stdev: %0.2f' % (mean(ds), stdev(ds)))


def read_out(i):
    filename = 'out/%d.out' % i
    with open(filename) as f:
        objval = float(f.readline())
        gap = float(f.readline())
        cycles = f.readline().strip()
        if cycles == 'None':
            cycles = []
        else:
            cycles = cycles.split('; ')
            cycles = [[int(v) for v in cycle.split(' ')] for cycle in cycles]
        return objval, gap, cycles

def count_two_cycle():
    count = 0
    for i in range(1, N+1):
        objval, gap, cycles = read_out(i)
        two_cycle = all([len(cycle) == 2 for cycle in cycles])
        if two_cycle:
            print('i:', i, 'objval:', objval)
            count += 1
    return count

def check_all():
    k = 5
    for i in range(1, N+1):
        print(i)
        A, C = read_instance(i)
        objval, _, cycles = read_out(i)
        check_cycles(A, C, k, cycles, objval)

def gen_output():
    for i in range(1, N+1):
        filename = 'out/%d.out' % i
        with open(filename, 'r') as f:
            f.readline() # objval
            f.readline() # gap
            cycles = f.readline().strip()
            print(cycles)

print_instance_stats()

# check_all()
# gen_output()
