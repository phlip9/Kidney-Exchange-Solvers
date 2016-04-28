from gurobipy import Model, GRB, tuplelist, LinExpr
from instance_gen import serialize, connected_components
import numpy as np
import time
from sys import argv

def read(filename):
    with open(filename, 'r') as f:
        lines = [[int(x) for x in line.split()] for line in f]
        n = lines[0][0]
        C = set(lines[1])
        A = np.array(lines[2:n+2])
        return A, C

def preprocess(A, C, k):
    """
    Split graph into Strongly Connected Components and remove
    cycle-less nodes.
    """
    subproblems = []
    n = A.shape[0]
    n_scc, scc = connected_components(A)
    # print('scc =', scc)
    if n_scc == 1:
        inv_map = [0]*n
        for i in range(n):
            inv_map[i] = i
        subproblems.append((A, C, inv_map))
    else:
        fwd_map = []
        scc_off = [0]*n_scc
        for i in range(n):
            j = scc[i]
            fwd_map.append(scc_off[j])
            scc_off[j] += 1
        # print('scc_off =', scc_off)
        # print('fwd_map =', fwd_map)

        for i in range(n_scc):
            mask = scc == i
            A_i = A[mask, ...][..., mask]
            inv_map = []
            for j in range(n):
                if scc[j] == i:
                    inv_map.append(j)
            C_i = set(fwd_map[c] for c in C if scc[c] == i)
            # print('i =', i)
            # print('A_i =')
            # print(A_i)
            # print('C_i =', C_i)
            # print('inv_map =', inv_map)
            subproblems.append((A_i, C_i, inv_map))

    # print('subproblems =', subproblems)

    return subproblems

def solve_instance(i):
    filename = 'phase1-processed/%d.in' % int(argv[1])
    cycles, objval = solve_file(filename)
    print('cycles:', cycles)
    print('objval:', objval)


def solve_file(filename, k):
    A, C = read(filename)
    return solve(A, C, k)

def solve(A, C, k):
    subproblems = preprocess(A, C, k)
    print('Decomposed into %d subproblems' % len(subproblems))
    cycles = []
    objval = 0.0
    for A_i, C_i, inv_map_i in subproblems:
        cycles_i, objval_i = solve_subproblem(A_i, C_i, inv_map_i, k)
        # print('cycles_i =', cycles_i)
        # print('objval_i =', objval_i)
        cycles.extend(cycles_i)
        objval += objval_i
    check_cycles(A, C, k, cycles, objval)
    return cycles, objval

def solve_subproblem(A, C, inv_map, k):
    cycles, objval = constantino(A, C, k)
    print('cycles_i (pre_inv) =', cycles)
    cycles = [[inv_map[c] for c in cycle] for cycle in cycles]
    return cycles, objval

def constantino(A, C, k):
    """
    Polynomial-sized CCMcP Edge-Extended Model
    See Constantino et al. (2013)
    """
    t_0 = time.clock()
    _ = '*'
    m = Model()
    m.modelsense = GRB.MAXIMIZE

    n = A.shape[0]
    vars = {}
    edges = tuplelist()

    print('[%.1f] Generating variables...' % (time.clock() - t_0))

    # Variables
    for l in range(n):
        for i in range(l, n):
            for j in range(l, n):
                if A[i, j] == 1:
                    e = (l, i, j)
                    edges.append(e)
                    w = 2 if j in C else 1
                    # var = m.addVar(vtype=GRB.BINARY, obj=w, name='x^%d_{%d,%d}' % e)
                    var = m.addVar(vtype=GRB.BINARY, obj=w)
                    vars[e] = var

        if l % 10 == 0 and l != 0:
            print('[%.1f] l = %d' % (time.clock() - t_0, l))

    m.update()

    print('[%.1f] Generated variables' % (time.clock() - t_0))
    print('[%.1f] Adding flow constraints...' % (time.clock() - t_0))

    # Constraint (2): Flow in = Flow out
    for l in range(n):
        for i in range(l, n):
            # Flow in
            lhs_vars = [vars[e] for e in edges.select(l, _, i)]
            ones = [1.0]*len(lhs_vars)
            lhs = LinExpr()
            lhs.addTerms(ones, lhs_vars)

            # Flow out
            rhs_vars = [vars[e] for e in edges.select(l, i, _)]
            ones = [1.0]*len(rhs_vars)
            rhs = LinExpr()
            rhs.addTerms(ones, rhs_vars)

            # Flow in = Flow out
            m.addConstr(lhs == rhs)

        if l % 10 == 0 and l != 0:
            print('[%.1f] l = %d' % (time.clock() - t_0, l))

    print('[%.1f] Added flow constraints' % (time.clock() - t_0))
    print('[%.1f] Adding cycle vertex constraints...' % (time.clock() - t_0))

    # Constraint (3): Use a vertex only once per cycle
    for i in range(n):
        c_vars = [vars[e] for e in edges.select(_, i, _)]
        ones = [1.0]*len(c_vars)
        expr = LinExpr()
        expr.addTerms(ones, c_vars)
        m.addConstr(expr <= 1.0)

        if i % 10 == 0 and i != 0:
            print('[%.1f] V_i = %d' % (time.clock() - t_0, i))

    print('[%.1f] Added cycle vertex constraints' % (time.clock() - t_0))
    print('[%.1f] Adding cycle cardinality constraints...' % (time.clock() - t_0))

    # Constraint (4): Limit cardinality of cycles to k
    for l in range(n):
        c_vars = [vars[e] for e in edges.select(l, _, _)]
        ones = [1.0]*len(c_vars)
        expr = LinExpr()
        expr.addTerms(ones, c_vars)
        m.addConstr(expr <= k)

        if l % 10 == 0 and l != 0:
            print('[%.1f] l = %d' % (time.clock() - t_0, l))

    print('[%.1f] Added cycle cardinality constraints' % (time.clock() - t_0))
    print('[%.1f] Adding cycle index constraints...' % (time.clock() - t_0))

    # Constraint (5): Cycle index is smallest vertex-index
    for l in range(n):
        rhs_vars = [vars[e] for e in edges.select(l, l, _)]
        ones = [1.0]*len(rhs_vars)
        rhs = LinExpr()
        rhs.addTerms(ones, rhs_vars)

        for i in range(l+1, n):
            lhs_vars = [vars[e] for e in edges.select(l, i, _)]
            if len(lhs_vars) > 0:
                ones = [1.0]*len(lhs_vars)
                lhs = LinExpr()
                lhs.addTerms(ones, lhs_vars)

                m.addConstr(lhs <= rhs)

        if l % 10 == 0 and l != 0:
            print('[%.1f] l = %d' % (time.clock() - t_0, l))

    print('[%.1f] Added cycle index constraints...' % (time.clock() - t_0))
    print('[%.1f] Begin Optimizing' % (time.clock() - t_0))

    m.optimize()
    m.update()

    print('[%.1f] Finished Optimizing' % (time.clock() - t_0))
    print('[%.1f] Building cycles...' % (time.clock() - t_0))

    cycles = []
    for l in range(n):
        c_edges = [e for e in edges.select(l, _, _) if vars[e].x == 1.0]
        n_edges = len(c_edges)

        if n_edges != 0:
            while len(c_edges) > 0:
                cycle = []
                e = c_edges.pop(0)
                i = e[1]
                j = e[2]
                cycle.append(i)
                k = 0
                while True:
                    e = c_edges[k]
                    if e[1] == j:
                        c_edges.pop(k)
                        k = 0
                        cycle.append(e[1])
                        j = e[2]
                        if j == i:
                            break
                    else:
                        k += 1
                cycles.append(cycle)

    print('[%.1f] Finished building cycles' % (time.clock() - t_0))

    return cycles, m.objval

def test():
    m = Model("mip1")

    x = m.addVar(vtype=GRB.BINARY, name='x')
    y = m.addVar(vtype=GRB.BINARY, name='y')
    z = m.addVar(vtype=GRB.BINARY, name='z')

    m.update()

    m.setObjective(x + y + 2 * z, GRB.MAXIMIZE)

    m.addConstr(x + 2 * y + 3 * z <= 4, 'c0')
    m.addConstr(x + y >= 1, 'c1')

    m.optimize()

    print('x =', x.x)
    print('y =', y.x)
    print('z =', z.x)
    print('objective =', m.objval)

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

def test_preprocess():
    A = np.array([
        [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    ])

    preprocess(A, [1, 4, 9, 11], 5)


if __name__ == '__main__':
    if len(argv) > 1 and int(argv[1]) in range(1, 493):
        solve_instance(int(argv[1]))
