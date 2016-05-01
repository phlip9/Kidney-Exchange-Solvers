from solvers import read
import numpy as np
from statistics import mean, median, stdev

N = 492

# instances = (read('phase1-processed/%d.in' % i)[0] for i in range(1, N + 1))
# ns = []
# ds = []
# for i in range(N):
    # A = next(instances)
    # n = A.shape[0]
    # ns.append(n)
    # d = 0.0
    # if n > 2:
        # d = np.sum(A)/float(n*n - n)
    # d = float(d)
    # ds.append(d)
    # print('[%d] : n = %d; d = %0.2f' % (i+1, n, d))

# print('n avg: %d, med: %0.2f, stdev: %0.2f' % (mean(ns), median(ns), stdev(ns)))
# print('d avg: %0.2f, stdev: %0.2f' % (mean(ds), stdev(ds)))


def read_out(i):
    filename = 'out/%d.out' % i
    with open(filename) as f:
        objval = float(f.readline())
        gap = float(f.readline())
        cycles = f.readline().split('; ')
        cycles = [cycle.split(' ') for cycle in cycles]
        return objval, gap, cycles

count = 0
for i in range(N):
    objval, gap, cycles = read_out(i+1)
    two_cycle = all([len(cycle) == 2 for cycle in cycles])
    if two_cycle:
        print('i:', i+1, 'objval:', objval)
        count += 1

print('count: %d' % count)
