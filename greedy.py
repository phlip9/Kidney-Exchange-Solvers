from sys import argv
import numpy as np


def read(filename):
    with open(filename, 'r') as f:
        lines = [[int(x) for x in line.split()] for line in f]
        n = lines[0][0]
        C = set(lines[1])
        A = np.array(lines[2:n+2])
        return A, C


def run(i, k):
    """
    Run our greedy algorithm on the ith instance with k max cycle length.
    """
    solve_greedy(i, k)


def solve_greedy(i, k, permutation):
    """
    permutation - a permutation of 1 to n
    """
    filename = 'phase1-processed/%d.in' % i
    A, C = read(filename)
    A_copy = np.copy(A)
    n = A.shape[0]
    matched = set()
    total_weight = 0
    cycles = []
    while True:
        start = None
        best_weight = 0
        best_cycle = None
        for i in range(n):
            if i in matched:
                continue
            cycle, weight = dfs_from(i, A, C, k, 5)
            if cycle is None:
                continue
            if weight > best_weight:
                start = i
                best_weight = weight
                best_cycle = cycle
        if best_cycle is None:
            break
        print("start: %d, weight: %d: %s" % (start, best_weight, str(best_cycle)))
        total_weight += best_weight
        for vertex in best_cycle:
            matched.add(vertex)
            for j in range(1, n):
                A[vertex][j] = 0
                A[j][vertex] = 0
        cycles.append(best_cycle)
    print(total_weight)
    check_cycles(A_copy, C, k, cycles, total_weight)


def dfs_from(i, A, C, k, L):
    n = A.shape[0]
    queue = [(j, [j]) for j in range(n) if A[i][j] == 1]
    found = []
    while len(queue) > 0:
        pos, path = queue.pop()
        for j in range(n):
            if A[pos][j] == 1:
                new_path = list(path)
                if j == i:
                    new_path.append(j)
                    found.append(new_path)
                    if len(found) == L:
                        return best_cycle(found, A, C)
                else:
                    new_path = list(path)
                    if j not in path:
                        new_path.append(j)
                        if len(new_path) < k:
                            queue.append((j, new_path))
    # base case
    return best_cycle(found, A, C)


def best_cycle(cycles, A, C):
    if len(cycles) == 0:
        return None, 0
    weights = []
    for cycle in cycles:
        weight = 0
        for vertex in cycle:
            if vertex in C:
                weight += 2
            else:
                weight += 1
        weights.append(weight)
    max_weight = 0
    best_cycle = None
    for i in range(len(weights)):
        if weights[i] > max_weight:
            max_weight = weights[i]
            best_cycle = cycles[i]
    return best_cycle, max_weight


def check_cycles(A, C, k, cycles, objval):
    n = A.shape[0]
    used = [False for i in range(n)]
    r_objval = 0.0
    for cycle in cycles:
        len_cycle = len(cycle)
        if len_cycle <= 1:
            print('ERROR: cycle of length <= 1 :', cycle)
        if len_cycle > k + 1:
            print('ERROR: cycle of length >=', k, ':', cycle)
        if len(set(cycle)) != len_cycle:
            print('ERROR: duplicate vertex in cycle :', cycle)

        for v in cycle:
            if used[v]:
                print('ERROR: cycle contains already-used vertex :', cycle, '(', v, ')')
            if v < 0 or v >= n:
                print('ERROR: vertex out of range:', v)
            used[v] = True
            r_objval += 2 if v in C else 1

        for i in range(1, len_cycle + 1):
            if A[cycle[i - 1], cycle[i % len_cycle]] != 1:
                print('ERROR: cycle contains nonexistent edge :', cycle, '(', cycle[i - 1], ',', cycle[i % len_cycle], ')')

    if r_objval != objval:
        print('ERROR: reported objective value != real objective value : r_objval =', r_objval, ', objval =', objval)

if __name__ == '__main__':
    if len(argv) > 1 and int(argv[1]) in range(1, 493):
        solve_greedy(int(argv[1]), 5)
