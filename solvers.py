from gurobipy import Model, GRB, tuplelist, LinExpr
from instance_gen import serialize, connected_components
import numpy as np
import time
from sys import argv
from os import path
from itertools import chain

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

        for i in range(n_scc):
            mask = scc == i
            A_i = A[mask, ...][..., mask]
            inv_map = []
            for j in range(n):
                if scc[j] == i:
                    inv_map.append(j)
            C_i = set(fwd_map[c] for c in C if scc[c] == i)
            subproblems.append((A_i, C_i, inv_map))

    return subproblems

def format_cycles(cycles):
    if len(cycles) == 0:
        return 'None'
    cycles = [' '.join(map(str, cycle)) for cycle in cycles]
    return '; '.join(cycles)

def output(i, cycles, objval, gap):
    filename = './out/%d.out' % i
    if path.isfile(filename):
        with open(filename, 'r') as f:
            objval2 = float(f.readline())
            if objval2 >= objval:
                return
    with open(filename, 'w') as f:
        f.write(str(objval) + '\n')
        f.write(str(gap) + '\n')
        f.write(format_cycles(cycles) + '\n')

def solve_instance(i, k, gap):
    print('Solving instance %d with gap %%%0.2f' % (i, gap))
    filename = 'phase1-processed/%d.in' % i
    cycles, objval = solve_file(filename, k, gap)
    print('cycles:', cycles)
    print('objval:', objval)
    # output(i, cycles, objval, gap)

def solve_file(filename, k, gap):
    A, C = read(filename)
    n = A.shape[0]
    d = np.sum(A)/(n*n - n)
    print('Solving', n, 'node graph with density', d)
    return solve(A, C, k, gap)

def solve(A, C, k, gap):
    subproblems = preprocess(A, C, k)
    print('Decomposed into %d subproblems' % len(subproblems))
    cycles = []
    objval = 0.0
    for A_i, C_i, inv_map_i in subproblems:
        cycles_i, objval_i = solve_subproblem(A_i, C_i, inv_map_i, k, gap)
        # print('cycles_i =', cycles_i)
        # print('objval_i =', objval_i)
        cycles.extend(cycles_i)
        objval += objval_i
    check_cycles(A, C, k, cycles, objval)
    return cycles, objval

def solve_subproblem(A, C, inv_map, k, gap):
    cycles, objval = constantino(A, C, k, gap)
    # cycles, objval = two_cycle(A, C, gap)
    # cycles, objval = lazy_cycle_constraint(A, C, k, gap)
    print('cycles_i (pre_inv) =', cycles)
    cycles = [[inv_map[c] for c in cycle] for cycle in cycles]
    return cycles, objval

def two_cycle(A, C, gap):
    """
    Solve high-vertex dense graphs by reduction to
    weighted matching ILP.
    """
    _ = '*'
    m = Model()
    m.modelsense = GRB.MAXIMIZE
    m.params.mipgap = gap
    m.params.timelimit = 60 * 60

    n = A.shape[0]
    vars = {}
    edges = tuplelist()

    # model as undirected graph
    for i in range(n):
        for j in range(i+1, n):
            if A[i, j] == 1 and A[j, i] == 1:
                e = (i, j)
                edges.append(e)
                w_i = 2 if i in C else 1
                w_j = 2 if j in C else 1
                w = w_i + w_j
                var = m.addVar(vtype=GRB.BINARY, obj=w)
                vars[e] = var

    m.update()

    # 2 cycle constraint <=> undirected flow <= 1
    for i in range(n):
        lhs = LinExpr()
        lhs_vars = [vars[e] for e in chain(edges.select(i, _), edges.select(_, i))]
        ones = [1.0]*len(lhs_vars)
        lhs.addTerms(ones, lhs_vars)

        m.addConstr(lhs <= 1)

    m.optimize()
    m.update()

    cycles = [list(e) for e in edges if vars[e].x == 1.0]
    return cycles, m.objval

def cycles_from_edges(c_edges):
    cycles = []
    n_edges = len(c_edges)
    if n_edges != 0:
        while len(c_edges) > 0:
            cycle = []
            e = c_edges.pop(0)
            i = e[0]
            j = e[1]
            cycle.append(i)
            k = 0
            while True:
                e = c_edges[k]
                if e[0] == j:
                    c_edges.pop(k)
                    k = 0
                    cycle.append(e[0])
                    j = e[1]
                    if j == i:
                        break
                else:
                    k += 1
            cycles.append(cycle)
    return cycles

def lazy_cycle_constraint(A, C, k, gap):
    """
    Lazily generate cycle constraints as potential feasible solutions
    are generated.
    """
    _ = '*'
    m = Model()
    m.modelsense = GRB.MAXIMIZE
    m.params.mipgap = gap
    m.params.timelimit = 5 * 60 * 60
    m.params.lazyconstraints = 1

    n = A.shape[0]
    edges = tuplelist()
    vars = {}

    for i in range(n):
        for j in range(n):
            if A[i, j] == 1:
                e = (i, j)
                edges.append(e)
                w = 2 if j in C else 1
                var = m.addVar(vtype=GRB.BINARY, obj=w)
                vars[e] = var

    m.update()

    # flow constraints
    for i in range(n):
        out_vars = [vars[e] for e in edges.select(i, _)]
        out_ones = [1.0]*len(out_vars)
        out_expr = LinExpr()
        out_expr.addTerms(out_ones, out_vars)

        in_vars = [vars[e] for e in edges.select(_, i)]
        in_ones = [1.0]*len(in_vars)
        in_expr = LinExpr()
        in_expr.addTerms(in_ones, in_vars)

        m.addConstr(in_expr <= 1)
        m.addConstr(out_expr == in_expr)

    m.update()

    ith_cycle = 0

    def callback(model, where):
        if where == GRB.Callback.MIPSOL:
            sols = model.cbGetSolution([vars[e] for e in edges])
            c_edges = [edges[i] for i in range(len(edges)) if sols[i] > 0.5]
            cycles = cycles_from_edges(c_edges)
            for cycle in cycles:
                len_cycle = len(cycle)
                if len_cycle > k:
                    cycle_vars = [vars[(cycle[i], cycle[(i+1) % len_cycle])] for i in range(len_cycle)]
                    ones = [1.0]*len(cycle_vars)
                    expr = LinExpr()
                    expr.addTerms(ones, cycle_vars)
                    model.cbLazy(expr <= len_cycle - 1)

    m.optimize(callback)
    m.update()

    c_edges = [e for e in edges if vars[e].x == 1.0]
    cycles = cycles_from_edges(c_edges)

    return cycles, m.objval

def constantino(A, C, k, gap):
    """
    Polynomial-sized CCMcP Edge-Extended Model
    See Constantino et al. (2013)
    """
    t_0 = time.clock()
    _ = '*'
    m = Model()
    m.modelsense = GRB.MAXIMIZE
    m.params.mipgap = gap
    # m.params.timelimit = 60 * 60
    # m.params.nodefilestart = 1.0
    # m.params.nodefiledir = './.nodefiledir'
    # m.params.presparsify = 0
    # m.params.presolve = 0

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
                    var = m.addVar(vtype=GRB.BINARY, obj=w)
                    vars[e] = var

        if l % 100 == 0 and l != 0:
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

        if l % 100 == 0 and l != 0:
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

        if i % 100 == 0 and i != 0:
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

        if l % 100 == 0 and l != 0:
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

        if l % 100 == 0 and l != 0:
            print('[%.1f] l = %d' % (time.clock() - t_0, l))

    print('[%.1f] Added cycle index constraints...' % (time.clock() - t_0))
    print('[%.1f] Begin Optimizing %d vertex model' % (time.clock() - t_0, n))

    m.optimize()
    m.update()

    print('[%.1f] Finished Optimizing' % (time.clock() - t_0))
    print('[%.1f] Building cycles...' % (time.clock() - t_0))

    cycles = []
    for l in range(n):
        c_edges = [(e[1], e[2]) for e in edges.select(l, _, _) if vars[e].x == 1.0]
        cycles.extend(cycles_from_edges(c_edges))

    print('[%.1f] Finished building cycles' % (time.clock() - t_0))

    return cycles, m.objval

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
        gap = 1e-4
        if len(argv) > 2:
            gap = float(argv[2])
        solve_instance(int(argv[1]), 5, gap)
