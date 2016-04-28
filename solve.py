from solvers import solve_instance

def read_n(filename):
    with open(filename) as f:
        return int(f.readline())

for i in range(1, 493):
    filename = 'phase1-processed/%d.in' % i
    n = read_n(filename)
    if n < 400:
        solve_instance(i, 5, 0.05)
